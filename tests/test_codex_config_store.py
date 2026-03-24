"""Tests for Codex config storage."""

import json
import tempfile
import unittest
from pathlib import Path

from packages.ai_api_tester_web.adaptor.config.defaults import DEFAULT_CODEX_PROVIDER_ID
from packages.ai_api_tester_web.adaptor.impl.codex_config_store import (
    apply_codex_preset,
    delete_codex_preset,
    load_codex_active_settings,
    load_codex_presets,
    upsert_codex_preset,
)


class CodexConfigStoreTests(unittest.TestCase):
    def test_upsert_codex_preset_saves_and_updates_by_name(self):
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
            self.assertEqual(load_codex_presets(presets_path)[0]["approval_policy"], "on-request")
            self.assertEqual(load_codex_presets(presets_path)[0]["sandbox_mode"], "workspace-write")

    def test_upsert_codex_preset_keeps_multiple_non_ascii_names_distinct(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            presets_path = Path(temp_dir) / "codex_presets.json"

            upsert_codex_preset(
                {"name": "Node_Alpha", "base_url": "https://hk.example.com/v1", "api_key": "key-hk"},
                presets_path,
            )
            result = upsert_codex_preset(
                {"name": "Node-Beta", "base_url": "https://jp.example.com/v1", "api_key": "key-jp"},
                presets_path,
            )

            self.assertEqual(len(result["presets"]), 2)
            self.assertEqual(result["presets"][0]["provider_id"], "Node_Alpha")
            self.assertEqual(result["presets"][1]["provider_id"], "Node-Beta")

    def test_delete_codex_preset_removes_target_item_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            presets_path = Path(temp_dir) / "codex_presets.json"

            upsert_codex_preset(
                {"name": "HK", "base_url": "https://hk.example.com/v1", "api_key": "key-hk"},
                presets_path,
            )
            upsert_codex_preset(
                {"name": "JP", "base_url": "https://jp.example.com/v1", "api_key": "key-jp"},
                presets_path,
            )

            result = delete_codex_preset("HK", presets_path)

            self.assertEqual(result["deleted_name"], "HK")
            self.assertEqual(len(result["presets"]), 1)
            self.assertEqual(result["presets"][0]["name"], "JP")
            self.assertEqual(load_codex_presets(presets_path)[0]["name"], "JP")

    def test_apply_codex_preset_reuses_current_provider_id(self):
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
                {"name": "HK-Node", "base_url": "https://api.example.com/v1", "api_key": "new-key", "approval_policy": "never", "sandbox_mode": "workspace-write"},
                presets_path,
                config_path,
                auth_path,
            )

            config_text = config_path.read_text(encoding="utf-8")
            auth_payload = json.loads(auth_path.read_text(encoding="utf-8"))

            self.assertIn('model_provider = "old-provider"', config_text)
            self.assertIn('[model_providers.old-provider]', config_text)
            self.assertIn('name = "HK-Node"', config_text)
            self.assertIn('base_url = "https://api.example.com/v1"', config_text)
            self.assertIn('approval_policy = "never"', config_text)
            self.assertIn('sandbox_mode = "workspace-write"', config_text)
            self.assertIn('model = "gpt-5.4"', config_text)
            self.assertEqual(auth_payload["OPENAI_API_KEY"], "new-key")
            self.assertEqual(result["active"]["name"], "HK-Node")
            self.assertEqual(result["active"]["provider_id"], "old-provider")
            self.assertEqual(result["active"]["approval_policy"], "never")
            self.assertEqual(result["active"]["sandbox_mode"], "workspace-write")

    def test_apply_codex_preset_uses_stable_default_provider_for_first_write(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            presets_path = temp_path / "codex_presets.json"
            config_path = temp_path / "config.toml"
            auth_path = temp_path / "auth.json"

            result = apply_codex_preset(
                {"name": "HK-Node", "base_url": "https://api.example.com/v1", "api_key": "new-key", "approval_policy": "never", "sandbox_mode": "danger-full-access"},
                presets_path,
                config_path,
                auth_path,
            )

            config_text = config_path.read_text(encoding="utf-8")
            auth_payload = json.loads(auth_path.read_text(encoding="utf-8"))

            self.assertIn(f'model_provider = "{DEFAULT_CODEX_PROVIDER_ID}"', config_text)
            self.assertIn(f'[model_providers.{DEFAULT_CODEX_PROVIDER_ID}]', config_text)
            self.assertIn('name = "HK-Node"', config_text)
            self.assertIn('base_url = "https://api.example.com/v1"', config_text)
            self.assertIn('approval_policy = "never"', config_text)
            self.assertIn('sandbox_mode = "danger-full-access"', config_text)
            self.assertEqual(auth_payload["OPENAI_API_KEY"], "new-key")
            self.assertEqual(result["active"]["name"], "HK-Node")
            self.assertEqual(result["active"]["provider_id"], DEFAULT_CODEX_PROVIDER_ID)
            self.assertEqual(result["active"]["approval_policy"], "never")
            self.assertEqual(result["active"]["sandbox_mode"], "danger-full-access")

    def test_load_codex_active_settings_reads_current_provider_and_auth(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            config_path = temp_path / "config.toml"
            auth_path = temp_path / "auth.json"
            config_path.write_text(
                'approval_policy = "never"\n'
                'sandbox_mode = "workspace-write"\n'
                'model_provider = "Prod_Node"\n\n'
                '[model_providers.Prod_Node]\n'
                'name = "Prod_Node"\n'
                'base_url = "https://prod.example.com/v1"\n'
                'wire_api = "responses"\n'
                'requires_openai_auth = true\n',
                encoding="utf-8",
            )
            auth_path.write_text(json.dumps({"OPENAI_API_KEY": "prod-key"}), encoding="utf-8")

            payload = load_codex_active_settings(config_path, auth_path)

            self.assertEqual(payload["name"], "Prod_Node")
            self.assertEqual(payload["provider_id"], "Prod_Node")
            self.assertEqual(payload["base_url"], "https://prod.example.com/v1")
            self.assertEqual(payload["approval_policy"], "never")
            self.assertEqual(payload["sandbox_mode"], "workspace-write")
            self.assertEqual(payload["api_key"], "prod-key")


if __name__ == "__main__":
    unittest.main()
