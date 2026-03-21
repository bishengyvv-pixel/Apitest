"""核心能力测试。"""

import tempfile
import unittest

from packages.ai_api_tester.adaptor.impl.api_gateway import (
    build_runtime,
    extract_assistant_text,
)
from packages.ai_api_tester.adaptor.impl.history_store import append_record
from packages.ai_api_tester.product.impl.service import get_statistics


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


if __name__ == "__main__":
    unittest.main()
