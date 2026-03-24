"""核心能力测试。"""

import tempfile
import unittest

from packages.ai_api_tester.adaptor.impl.api_gateway import (
    UpstreamServiceError,
    _build_upstream_http_error,
    _parse_stream_events,
    _parse_upstream_json_response,
    build_runtime,
    extract_assistant_text,
)
from packages.ai_api_tester.adaptor.impl.history_store import append_record
from packages.ai_api_tester.product.impl.service import get_statistics
from packages.ai_api_tester.shell.requirements import URL_ERROR


class AiApiTesterTests(unittest.TestCase):
    """验证核心业务逻辑。"""

    def test_build_runtime_normalizes_base_url(self):
        """基础配置应被规范化。"""
        runtime = build_runtime(
            {
                "base_url": "https://example.com/v1/",
                "api_key": "test-key",
                "timeout_seconds": 12,
                "max_tokens": 256,
            }
        )

        self.assertEqual(runtime["base_url"], "https://example.com/v1")
        self.assertEqual(runtime["api_key"], "test-key")
        self.assertEqual(runtime["timeout_seconds"], 12)
        self.assertEqual(runtime["max_tokens"], 256)
        self.assertEqual(runtime["user_agent"], "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")

    def test_build_runtime_accepts_custom_user_agent(self):
        """可通过配置覆盖默认客户端标识。"""
        runtime = build_runtime({"user_agent": "My-Test-Client/2.0"})
        self.assertEqual(runtime["user_agent"], "My-Test-Client/2.0")

    def test_extract_assistant_text_supports_rich_parts(self):
        """多段内容响应应被拼接成纯文本。"""
        payload = {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "text", "text": "第一段"},
                            {"type": "image_url", "image_url": {"url": "ignored"}},
                            {"type": "text", "text": "第二段"},
                        ]
                    }
                }
            ]
        }

        self.assertEqual(extract_assistant_text(payload), "第一段\n第二段")

    def test_parse_stream_events_reassembles_text_and_usage(self):
        """SSE chunks should be normalized into a regular payload."""
        raw_body = (
            'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":", world"}}]}\n\n'
            'data: {"choices":[{"delta":{}}],"usage":{"prompt_tokens":12,"completion_tokens":8,"total_tokens":20}}\n\n'
            'data: [DONE]\n\n'
        )

        payload = _parse_stream_events(raw_body)

        self.assertEqual(extract_assistant_text(payload), "Hello, world")
        self.assertEqual(payload["usage"]["total_tokens"], 20)

    def test_parse_upstream_json_response_reports_empty_body(self):
        """Empty responses should become actionable upstream errors."""
        runtime = build_runtime({"base_url": "https://example.com/v1"})

        with self.assertRaises(UpstreamServiceError) as error_context:
            _parse_upstream_json_response(runtime, "", "application/json", "/models")

        self.assertEqual(error_context.exception.diagnostic_code, "empty_response_body")
        self.assertEqual(error_context.exception.details["path"], "/models")
        self.assertIn("baseurl", str(error_context.exception))

    def test_parse_upstream_json_response_reports_invalid_json_body(self):
        """Non-JSON responses should point users back to the API base URL."""
        runtime = build_runtime({"base_url": "https://example.com/v1"})

        with self.assertRaises(UpstreamServiceError) as error_context:
            _parse_upstream_json_response(runtime, "<html>login</html>", "text/html", "/models")

        self.assertEqual(error_context.exception.diagnostic_code, "invalid_json_response")
        self.assertEqual(error_context.exception.details["content_type"], "text/html")
        self.assertIn("/v1", str(error_context.exception))

    def test_statistics_are_aggregated_from_history(self):
        """统计结果应正确计算平均耗时和 token。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = f"{temp_dir}/history.jsonl"
            runtime = {"history_path": history_path}

            append_record(
                runtime,
                {
                    "kind": "chat",
                    "model": "gpt-4o-mini",
                    "prompt": "你好",
                    "response_text": "你好，有什么可以帮你？",
                    "elapsed_seconds": 1.2,
                    "created_at": "2026-03-20T10:00:00Z",
                    "usage": {
                        "prompt_tokens": 10,
                        "completion_tokens": 20,
                        "total_tokens": 30,
                    },
                },
            )
            append_record(
                runtime,
                {
                    "kind": "vision",
                    "model": "gpt-4.1-mini",
                    "prompt": "这张图是什么？",
                    "response_text": "这是一张测试图片。",
                    "elapsed_seconds": 2.4,
                    "created_at": "2026-03-20T11:00:00Z",
                    "usage": {
                        "prompt_tokens": 15,
                        "completion_tokens": 25,
                        "total_tokens": 40,
                    },
                },
            )

            stats = get_statistics(runtime)

            self.assertEqual(stats["session_count"], 2)
            self.assertEqual(stats["average_duration_seconds"], 1.8)
            self.assertEqual(stats["total_tokens"], 70)
            self.assertEqual(stats["prompt_tokens"], 25)
            self.assertEqual(stats["completion_tokens"], 45)
            self.assertEqual(stats["kind_breakdown"]["chat"], 1)
            self.assertEqual(stats["kind_breakdown"]["vision"], 1)
            self.assertEqual(stats["latest_session_at"], "2026-03-20T11:00:00Z")

    def test_cloudflare_1010_error_is_classified_with_actionable_message(self):
        """Cloudflare 1010 应被识别成上游拦截而非普通 403。"""
        runtime = build_runtime({"base_url": "https://api-vip.codex-for.me/v1"})
        error = URL_ERROR.HTTPError(
            url="https://api-vip.codex-for.me/v1/models",
            code=403,
            msg="Forbidden",
            hdrs=None,
            fp=None,
        )

        classified = _build_upstream_http_error(
            runtime,
            error,
            '{"title":"Error 1010: Access denied","status":403,"detail":"The site owner has blocked access based on your browser\\u0027s signature.","error_code":1010,"error_name":"browser_signature_banned","cloudflare_error":true,"retryable":false,"owner_action_required":true,"zone":"api-vip.codex-for.me"}',
        )

        self.assertIsInstance(classified, UpstreamServiceError)
        self.assertEqual(classified.status_code, 403)
        self.assertEqual(classified.diagnostic_code, "cloudflare_browser_signature_banned")
        self.assertIn("Cloudflare", str(classified))
        self.assertIn("apikey 错误", str(classified))


if __name__ == "__main__":
    unittest.main()



