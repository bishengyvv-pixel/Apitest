"""Web 产品层测试。"""

import unittest
from unittest.mock import patch

from packages.ai_api_tester_web.product.impl.service import (
    build_bootstrap_payload,
    build_models_payload,
    extract_connection_settings,
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

    def test_build_bootstrap_payload_contains_default_image_url(self):
        """前端启动信息应包含默认图片资源。"""
        payload = build_bootstrap_payload()
        self.assertIn("default_vision_image_url", payload)
        self.assertEqual(payload["default_vision_image_url"], "/assets/default-vision.png")

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


if __name__ == "__main__":
    unittest.main()
