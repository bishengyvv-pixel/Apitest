"""Codex 配置存储测试。"""

import json
import tempfile
import unittest
from pathlib import Path

from packages.ai_api_tester_web.adaptor.impl.codex_config_store import (
    apply_codex_preset,
    load_codex_active_settings,
    load_codex_presets,
    upsert_codex_preset,
)


class CodexConfigStoreTests(unittest.TestCase):
    """验证 Codex 预设保存与配置写回。"""

    def test_upsert_codex_preset_saves_and_updates_by_name(self):
        """同名预设应被覆盖而不是重复追加。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            presets_path = Path(temp_dir) / "codex_presets.json"

            upsert_codex_preset(
                {"name": "HK", "base_url": "https://one.example.com/v1", "api_key": "key-1"},
                presets_path,
            )
            result = upsert_codex_preset(
                {"name": "HK", "base_url": "https://two.example.com/v1", "api_key": "key-2"},
                presets_path,
            )

            self.assertEqual(len(result["presets"]), 1)
            self.assertEqual(result["presets"][0]["base_url"], "https://two.example.com/v1")
            self.assertEqual(load_codex_presets(presets_path)[0]["api_key"], "key-2")

    def test_apply_codex_preset_updates_config_and_auth_files(self):
        """应用预设时应同时更新 config.toml 和 auth.json。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            presets_path = temp_path / "codex_presets.json"
            config_path = temp_path / "config.toml"
            auth_path = temp_path / "auth.json"
            config_path.write_text(
                'model_provider = "old-provider"\n'
                'model = "gpt-5.4"\n'
                'model_reasoning_effort = "high"\n\n'
                '[model_providers.old-provider]\n'
                'name = "old"\n'
                'base_url = "https://old.example.com/v1"\n'
                'wire_api = "responses"\n'
                'requires_openai_auth = true\n',
                encoding="utf-8",
            )
            auth_path.write_text(json.dumps({"OPENAI_API_KEY": "old-key"}), encoding="utf-8")

            result = apply_codex_preset(
                {"name": "HK Node", "base_url": "https://api.example.com/v1", "api_key": "new-key"},
                presets_path,
                config_path,
                auth_path,
            )

            config_text = config_path.read_text(encoding="utf-8")
            auth_payload = json.loads(auth_path.read_text(encoding="utf-8"))

            self.assertIn('model_provider = "preset-hk-node"', config_text)
            self.assertIn('[model_providers.preset-hk-node]', config_text)
            self.assertIn('name = "HK Node"', config_text)
            self.assertIn('base_url = "https://api.example.com/v1"', config_text)
            self.assertIn('model = "gpt-5.4"', config_text)
            self.assertEqual(auth_payload["OPENAI_API_KEY"], "new-key")
            self.assertEqual(result["active"]["name"], "HK Node")

    def test_load_codex_active_settings_reads_current_provider_and_auth(self):
        """活动配置应从 config.toml 和 auth.json 合并读取。"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "config.toml"
            auth_path = temp_path / "auth.json"
            config_path.write_text(
                'model_provider = "preset-prod"\n\n'
                '[model_providers.preset-prod]\n'
                'name = "生产环境"\n'
                'base_url = "https://prod.example.com/v1"\n'
                'wire_api = "responses"\n'
                'requires_openai_auth = true\n',
                encoding="utf-8",
            )
            auth_path.write_text(json.dumps({"OPENAI_API_KEY": "prod-key"}), encoding="utf-8")

            payload = load_codex_active_settings(config_path, auth_path)

            self.assertEqual(payload["name"], "生产环境")
            self.assertEqual(payload["provider_id"], "preset-prod")
            self.assertEqual(payload["base_url"], "https://prod.example.com/v1")
            self.assertEqual(payload["api_key"], "prod-key")


if __name__ == "__main__":
    unittest.main()
