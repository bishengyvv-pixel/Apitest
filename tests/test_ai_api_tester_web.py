"""Web 产品层测试。"""

import unittest
from unittest.mock import patch

from packages.ai_api_tester.adaptor.impl.api_gateway import UpstreamServiceError
from packages.ai_api_tester_web.product.impl.service import (
    build_bootstrap_payload,
    build_models_payload,
    extract_codex_preset,
    extract_connection_settings,
    handle_api_request,
    resolve_selected_model,
)


class WebServiceTests(unittest.TestCase):
    """验证 Web 层纯业务逻辑。"""

    def test_extract_connection_settings_requires_base_url_and_api_key(self):
        """连接字段应按最小必填约束校验。"""
        settings = extract_connection_settings(
            {"base_url": " https://example.com/v1 ", "api_key": " test-key "}
        )

        self.assertEqual(settings["base_url"], "https://example.com/v1")
        self.assertEqual(settings["api_key"], "test-key")

    def test_extract_codex_preset_requires_name_base_url_and_api_key(self):
        """Codex 预设应要求名称与连接信息完整。"""
        preset = extract_codex_preset(
            {"name": " HK-Node ", "base_url": " https://example.com/v1 ", "api_key": " test-key ", "approval_policy": "never", "sandbox_mode": "workspace-write"}
        )

        self.assertEqual(preset["name"], "HK-Node")
        self.assertEqual(preset["base_url"], "https://example.com/v1")
        self.assertEqual(preset["api_key"], "test-key")
        self.assertEqual(preset["approval_policy"], "never")
        self.assertEqual(preset["sandbox_mode"], "workspace-write")

    def test_extract_codex_preset_rejects_invalid_name_characters(self):
        with self.assertRaisesRegex(ValueError, "Preset name only supports"):
            extract_codex_preset(
                {"name": "HK Node", "base_url": "https://example.com/v1", "api_key": "test-key"}
            )

    def test_extract_codex_preset_rejects_invalid_approval_policy(self):
        with self.assertRaisesRegex(ValueError, "approval_policy"):
            extract_codex_preset(
                {
                    "name": "HK-Node",
                    "base_url": "https://example.com/v1",
                    "api_key": "test-key",
                    "approval_policy": "always",
                }
            )

    @patch("packages.ai_api_tester_web.product.impl.service.load_codex_active_settings")
    @patch("packages.ai_api_tester_web.product.impl.service.load_codex_presets")
    def test_build_bootstrap_payload_contains_codex_metadata(self, mock_load_presets, mock_load_active):
        """前端启动信息应带上 Codex 预设与当前配置。"""
        mock_load_presets.return_value = [{"name": "preset-a", "base_url": "https://example.com/v1"}]
        mock_load_active.return_value = {"name": "preset-a", "base_url": "https://example.com/v1"}

        payload = build_bootstrap_payload()

        self.assertIn("default_vision_image_url", payload)
        self.assertEqual(payload["default_vision_image_url"], "/assets/default-vision.png")
        self.assertEqual(payload["codex_presets"][0]["name"], "preset-a")
        self.assertEqual(payload["codex_active"]["name"], "preset-a")

    @patch("packages.ai_api_tester_web.product.impl.service.fetch_models")
    def test_resolve_selected_model_prefers_client_selection(self, mock_fetch_models):
        """用户已选模型时不应再次请求模型列表。"""
        result = resolve_selected_model({"base_url": "x", "api_key": "y"}, "gpt-picked")
        self.assertEqual(result, "gpt-picked")
        mock_fetch_models.assert_not_called()

    @patch("packages.ai_api_tester_web.product.impl.service.fetch_models")
    def test_resolve_selected_model_falls_back_to_first_available_model(self, mock_fetch_models):
        """未选择模型时应自动回退到列表首项。"""
        mock_fetch_models.return_value = {
            "models": [
                {"id": "gpt-4o-mini"},
                {"id": "gpt-4.1-mini"},
            ]
        }

        result = resolve_selected_model({"base_url": "x", "api_key": "y"}, "")
        self.assertEqual(result, "gpt-4o-mini")

    @patch("packages.ai_api_tester_web.product.impl.service.fetch_models")
    def test_build_models_payload_sets_selected_model(self, mock_fetch_models):
        """模型列表响应应带回默认选中项。"""
        mock_fetch_models.return_value = {
            "models": [
                {"id": "gpt-4o-mini", "owned_by": "openai", "object": "model"},
            ]
        }

        payload = build_models_payload({"base_url": "x", "api_key": "y"})
        self.assertEqual(payload["selected_model"], "gpt-4o-mini")
        self.assertEqual(len(payload["models"]), 1)

    @patch("packages.ai_api_tester_web.product.impl.service.apply_selected_codex_preset")
    def test_handle_api_request_can_apply_codex_preset(self, mock_apply_selected_codex_preset):
        """应用 Codex 预设的路由应返回更新结果。"""
        mock_apply_selected_codex_preset.return_value = {
            "message": "已应用",
            "active": {"name": "preset-a"},
            "presets": [{"name": "preset-a"}],
        }

        status_code, payload = handle_api_request(
            "POST",
            "/api/codex-apply",
            {"name": "preset-a", "base_url": "https://example.com/v1", "api_key": "test"},
            {"default_image_path": "unused"},
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(payload["active"]["name"], "preset-a")

    @patch("packages.ai_api_tester_web.product.impl.service.remove_codex_preset")
    def test_handle_api_request_can_delete_codex_preset(self, mock_remove_codex_preset):
        """删除 Codex 预设的路由应返回更新结果。"""
        mock_remove_codex_preset.return_value = {
            "message": "已删除",
            "deleted_name": "preset-a",
            "presets": [{"name": "preset-b"}],
        }

        status_code, payload = handle_api_request(
            "DELETE",
            "/api/codex-presets",
            {"name": "preset-a"},
            {"default_image_path": "unused"},
        )

        self.assertEqual(status_code, 200)
        self.assertEqual(payload["deleted_name"], "preset-a")

    @patch("packages.ai_api_tester_web.product.impl.service.run_default_text")
    def test_handle_api_request_maps_upstream_error_to_502(self, mock_run_default_text):
        """上游故障应返回 502 与诊断信息。"""
        mock_run_default_text.side_effect = UpstreamServiceError(
            "上游接口返回 HTTP 403，Cloudflare 已拒绝当前客户端签名。",
            status_code=403,
            diagnostic_code="cloudflare_browser_signature_banned",
            details={"host": "api-vip.codex-for.me"},
        )

        status_code, payload = handle_api_request(
            "POST",
            "/api/default-text",
            {"base_url": "https://example.com/v1", "api_key": "test"},
            {"default_image_path": "unused"},
        )

        self.assertEqual(status_code, 502)
        self.assertEqual(payload["upstream_status_code"], 403)
        self.assertEqual(payload["diagnostic_code"], "cloudflare_browser_signature_banned")


if __name__ == "__main__":
    unittest.main()

