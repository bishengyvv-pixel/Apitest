"""GUI 侧可测试的纯逻辑能力。"""

import unittest

from packages.ai_api_tester_gui.product.impl.presenter import (
    build_model_choices_from_result,
    build_model_view_model,
    build_stats_view_model,
    extract_service_settings,
    merge_settings,
)


class GuiPresenterTests(unittest.TestCase):
    """验证 GUI 展示层的纯逻辑函数。"""

    def test_merge_settings_prefers_cli_over_saved(self):
        """命令行初值应覆盖已保存配置。"""
        merged = merge_settings(
            {"base_url": "https://cli.example.com", "timeout_seconds": "30"},
            {"base_url": "https://saved.example.com", "api_key": "saved-key"},
        )

        self.assertEqual(merged["base_url"], "https://cli.example.com")
        self.assertEqual(merged["api_key"], "saved-key")
        self.assertEqual(merged["timeout_seconds"], "30")

    def test_extract_service_settings_keeps_whitelisted_keys(self):
        """界面表单应只保留核心配置字段。"""
        settings = extract_service_settings(
            {
                "base_url": " https://example.com ",
                "default_model": " gpt-test ",
                "extra": "ignored",
            }
        )

        self.assertEqual(settings["base_url"], "https://example.com")
        self.assertEqual(settings["default_model"], "gpt-test")
        self.assertNotIn("extra", settings)

    def test_build_model_view_model_extracts_choices(self):
        """模型视图模型应输出表格行和选择项。"""
        payload = {
            "base_url": "https://example.com",
            "models": [
                {"id": "gpt-4o-mini", "owned_by": "openai", "object": "model"},
                {"id": "gpt-4.1-mini", "owned_by": "openai", "object": "model"},
            ],
        }

        view_model = build_model_view_model(payload)
        self.assertEqual(view_model["count"], 2)
        self.assertEqual(view_model["choices"], ["gpt-4o-mini", "gpt-4.1-mini"])

    def test_build_model_choices_from_result_returns_single_model(self):
        """对话结果应能回填模型选择。"""
        self.assertEqual(build_model_choices_from_result({"model": "gpt-4o-mini"}), ["gpt-4o-mini"])

    def test_build_stats_view_model_formats_summary(self):
        """统计视图模型应保留摘要字段。"""
        view_model = build_stats_view_model(
            {
                "history_path": "data/history.jsonl",
                "session_count": 5,
                "average_duration_seconds": 1.23,
                "total_tokens": 500,
                "latest_session_at": "2026-03-20T12:00:00Z",
                "prompt_tokens": 200,
                "completion_tokens": 300,
                "kind_breakdown": {"chat": 3, "vision": 2},
                "per_model": [
                    {
                        "model": "gpt-4o-mini",
                        "session_count": 3,
                        "average_duration_seconds": 1.1,
                        "total_tokens": 200,
                    }
                ],
            }
        )

        self.assertEqual(view_model["summary"]["session_count"], "5")
        self.assertEqual(view_model["summary"]["vision_count"], "2")
        self.assertEqual(view_model["per_model_rows"][0]["model"], "gpt-4o-mini")


if __name__ == "__main__":
    unittest.main()
