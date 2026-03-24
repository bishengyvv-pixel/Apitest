"""Local read/write for Codex presets and config files."""

import re

from ...adaptor.config.defaults import (
    CODEX_APPROVAL_POLICY_OPTIONS,
    CODEX_SANDBOX_MODE_OPTIONS,
    DEFAULT_CODEX_APPROVAL_POLICY,
    DEFAULT_CODEX_PRESETS_PATH,
    DEFAULT_CODEX_PROVIDER_ID,
    DEFAULT_CODEX_SANDBOX_MODE,
)
from ...shell.requirements import JSON, PATH


PRESET_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")
PRESET_NAME_MESSAGE = "Preset name only supports English letters, numbers, underscore, and hyphen."
APPROVAL_POLICY_MESSAGE = 'approval_policy only supports "never" and "on-request".'
SANDBOX_MODE_MESSAGE = 'sandbox_mode only supports "danger-full-access" and "workspace-write".'


def load_codex_presets(path=None):
    """Load saved Codex presets from the project file."""
    target_path = _resolve_presets_path(path)
    if not target_path.exists():
        return []

    try:
        payload = JSON.loads(target_path.read_text(encoding="utf-8"))
    except (JSON.JSONDecodeError, OSError):
        return []

    source_items = payload
    if isinstance(payload, dict):
        source_items = payload.get("presets")

    if not isinstance(source_items, list):
        return []

    presets = []
    for item in source_items:
        normalized = _normalize_preset(item, require_all=False)
        if normalized.get("name"):
            presets.append(normalized)
    return presets


def save_codex_presets(presets, path=None):
    """Save the project-local Codex preset list."""
    target_path = _resolve_presets_path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    normalized_items = []
    for item in presets or []:
        normalized = _normalize_preset(item, require_all=False)
        if normalized.get("name"):
            normalized_items.append(normalized)

    payload = {"presets": normalized_items}
    target_path.write_text(JSON.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return normalized_items


def upsert_codex_preset(payload, path=None):
    """Insert or update one preset by name."""
    preset = _normalize_preset(payload, require_all=True)
    presets = load_codex_presets(path)
    replaced = False

    for index, item in enumerate(presets):
        if item["name"] == preset["name"]:
            presets[index] = preset
            replaced = True
            break

    if not replaced:
        presets.append(preset)

    saved_items = save_codex_presets(presets, path)
    return {
        "preset": preset,
        "presets": saved_items,
        "message": f"Saved Codex preset: {preset['name']}",
    }


def delete_codex_preset(name, path=None):
    """Delete one preset by name."""
    preset_name = _clean_text(name)
    if not preset_name:
        raise ValueError("Preset name is required.")

    presets = load_codex_presets(path)
    remaining_items = [item for item in presets if item["name"] != preset_name]

    if len(remaining_items) == len(presets):
        raise ValueError(f"Preset not found: {preset_name}")

    saved_items = save_codex_presets(remaining_items, path)
    return {
        "deleted_name": preset_name,
        "presets": saved_items,
        "message": f"Deleted Codex preset: {preset_name}",
    }


def load_codex_active_settings(config_path=None, auth_path=None):
    """Read the currently active Codex config."""
    resolved_config_path = _resolve_codex_config_path(config_path)
    resolved_auth_path = _resolve_codex_auth_path(auth_path)
    config_text = ""
    if resolved_config_path.exists():
        try:
            config_text = resolved_config_path.read_text(encoding="utf-8")
        except OSError:
            config_text = ""

    provider_id = _read_root_string(config_text, "model_provider")
    provider_section = ""
    if provider_id:
        provider_section = _read_section(config_text, f"model_providers.{provider_id}")

    auth_payload = _load_json_object(resolved_auth_path)
    return {
        "name": _read_section_string(provider_section, "name") or provider_id,
        "provider_id": provider_id,
        "base_url": _read_section_string(provider_section, "base_url"),
        "approval_policy": _normalize_choice(
            _read_root_string(config_text, "approval_policy"),
            CODEX_APPROVAL_POLICY_OPTIONS,
        ),
        "sandbox_mode": _normalize_choice(
            _read_root_string(config_text, "sandbox_mode"),
            CODEX_SANDBOX_MODE_OPTIONS,
        ),
        "api_key": _clean_text(auth_payload.get("OPENAI_API_KEY")),
        "config_path": str(resolved_config_path),
        "auth_path": str(resolved_auth_path),
    }


def apply_codex_preset(payload, presets_path=None, config_path=None, auth_path=None):
    """Apply one preset to the user's Codex config."""
    preset = _normalize_preset(payload, require_all=True)
    upsert_codex_preset(preset, presets_path)

    resolved_config_path = _resolve_codex_config_path(config_path)
    resolved_auth_path = _resolve_codex_auth_path(auth_path)
    applied_preset = dict(preset)
    applied_preset["provider_id"] = _resolve_apply_provider_id(resolved_config_path)
    _write_codex_config(applied_preset, resolved_config_path)
    _write_codex_auth(applied_preset, resolved_auth_path)

    return {
        "preset": applied_preset,
        "presets": load_codex_presets(presets_path),
        "active": load_codex_active_settings(resolved_config_path, resolved_auth_path),
        "message": f"Applied preset {preset['name']} to Codex config.",
    }


def _resolve_apply_provider_id(config_path):
    """Reuse the active provider_id when available to keep Codex history stable."""
    config_text = ""
    if config_path.exists():
        try:
            config_text = config_path.read_text(encoding="utf-8")
        except OSError:
            config_text = ""

    provider_id = _read_root_string(config_text, "model_provider")
    if provider_id:
        return provider_id
    return DEFAULT_CODEX_PROVIDER_ID


def _write_codex_config(preset, target_path):
    """Update Codex config.toml with minimal changes."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    current_text = ""
    if target_path.exists():
        try:
            current_text = target_path.read_text(encoding="utf-8")
        except OSError:
            current_text = ""

    if not current_text.strip():
        current_text = (
            'model = "gpt-5.4"\n'
            'model_reasoning_effort = "high"\n'
            'disable_response_storage = false\n'
        )

    provider_id = preset["provider_id"]
    updated_text = _upsert_root_string(current_text, "sandbox_mode", preset["sandbox_mode"])
    updated_text = _upsert_root_string(updated_text, "approval_policy", preset["approval_policy"])
    updated_text = _upsert_root_string(updated_text, "model_provider", provider_id)
    updated_text = _upsert_provider_block(updated_text, provider_id, preset["name"], preset["base_url"])
    target_path.write_text(updated_text.rstrip() + "\n", encoding="utf-8")


def _write_codex_auth(preset, target_path):
    """Update OPENAI_API_KEY in Codex auth.json."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _load_json_object(target_path)
    payload["OPENAI_API_KEY"] = preset["api_key"]
    target_path.write_text(JSON.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _upsert_root_string(text, key, value):
    """Update one top-level TOML string key."""
    lines = text.splitlines()
    first_section_index = len(lines)
    for index, line in enumerate(lines):
        if line.strip().startswith("["):
            first_section_index = index
            break

    target_line = f'{key} = "{_escape_toml_string(value)}"'
    for index in range(first_section_index):
        if lines[index].strip().startswith(f"{key} ="):
            lines[index] = target_line
            return "\n".join(lines)

    lines.insert(0, target_line)
    return "\n".join(lines)


def _upsert_provider_block(text, provider_id, name, base_url):
    """Update or append one provider TOML block."""
    header = _build_provider_header(provider_id)
    block_lines = [
        header,
        f'name = "{_escape_toml_string(name)}"',
        f'base_url = "{_escape_toml_string(base_url)}"',
        'wire_api = "responses"',
        'requires_openai_auth = true',
    ]
    lines = text.splitlines()

    start_index = -1
    end_index = len(lines)
    for index, line in enumerate(lines):
        if line.strip() == header:
            start_index = index
            continue
        if start_index >= 0 and line.strip().startswith("["):
            end_index = index
            break

    if start_index >= 0:
        replacement = lines[:start_index] + block_lines + lines[end_index:]
        return "\n".join(replacement)

    if lines and lines[-1].strip():
        lines.append("")
    lines.extend(block_lines)
    return "\n".join(lines)


def _read_root_string(text, key):
    """Read one top-level TOML string key."""
    lines = str(text or "").splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("["):
            break
        if stripped.startswith(f"{key} ="):
            return _parse_toml_string(stripped.split("=", 1)[1])
    return ""


def _read_section(text, section_name):
    """Read the raw body of one TOML section."""
    if section_name.startswith("model_providers."):
        provider_id = section_name.split(".", 1)[1]
        header = _build_provider_header(provider_id)
    else:
        header = f"[{section_name}]"
    lines = str(text or "").splitlines()
    collected = []
    recording = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("["):
            if recording:
                break
            if stripped == header:
                recording = True
                continue
        if recording:
            collected.append(line)

    return "\n".join(collected)


def _read_section_string(section_text, key):
    """Read one string key from a TOML section body."""
    for line in str(section_text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{key} ="):
            return _parse_toml_string(stripped.split("=", 1)[1])
    return ""


def _parse_toml_string(value):
    """Parse a basic TOML string literal."""
    text = str(value or "").strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    return text.replace('\\"', '"').replace('\\\\', '\\').strip()


def _escape_toml_string(value):
    """Escape a value for a TOML string literal."""
    return str(value or "").replace('\\', '\\\\').replace('"', '\\"')


def _load_json_object(path):
    """Safely read a JSON object."""
    if not path.exists():
        return {}
    try:
        payload = JSON.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except (JSON.JSONDecodeError, OSError):
        return {}
    return {}


def _normalize_choice(value, allowed_values, fallback=""):
    """Normalize one enum-like string field."""
    text = _clean_text(value)
    if text in allowed_values:
        return text
    return fallback


def _normalize_preset(payload, require_all):
    """Normalize preset fields."""
    source = payload or {}
    approval_policy = _clean_text(source.get("approval_policy"))
    sandbox_mode = _clean_text(source.get("sandbox_mode"))
    preset = {
        "name": _clean_text(source.get("name")),
        "base_url": _clean_text(source.get("base_url")).rstrip("/"),
        "api_key": _clean_text(source.get("api_key")),
        "approval_policy": _normalize_choice(
            approval_policy,
            CODEX_APPROVAL_POLICY_OPTIONS,
            DEFAULT_CODEX_APPROVAL_POLICY,
        ),
        "sandbox_mode": _normalize_choice(
            sandbox_mode,
            CODEX_SANDBOX_MODE_OPTIONS,
            DEFAULT_CODEX_SANDBOX_MODE,
        ),
    }
    preset["provider_id"] = preset["name"]

    if require_all:
        if not preset["name"]:
            raise ValueError("Preset name is required.")
        if not PRESET_NAME_PATTERN.fullmatch(preset["name"]):
            raise ValueError(PRESET_NAME_MESSAGE)
        if not preset["base_url"]:
            raise ValueError("base_url is required.")
        if not preset["api_key"]:
            raise ValueError("api_key is required.")
        if approval_policy and approval_policy not in CODEX_APPROVAL_POLICY_OPTIONS:
            raise ValueError(APPROVAL_POLICY_MESSAGE)
        if sandbox_mode and sandbox_mode not in CODEX_SANDBOX_MODE_OPTIONS:
            raise ValueError(SANDBOX_MODE_MESSAGE)

    return preset


def _build_provider_header(provider_id):
    """Build the TOML section header for one provider."""
    return f"[model_providers.{_format_toml_key_segment(provider_id)}]"


def _format_toml_key_segment(value):
    """Format one TOML dotted-key segment."""
    text = _clean_text(value)
    if text and _is_bare_toml_key(text):
        return text
    return f'"{_escape_toml_string(text)}"'


def _is_bare_toml_key(value):
    """Return whether the text can be used as a bare TOML key."""
    for char in str(value or ""):
        is_ascii_letter = ("a" <= char <= "z") or ("A" <= char <= "Z")
        is_digit = "0" <= char <= "9"
        if is_ascii_letter or is_digit or char in "-_":
            continue
        return False
    return bool(str(value or ""))


def _clean_text(value):
    """Normalize arbitrary input into a trimmed string."""
    if value is None:
        return ""
    return str(value).strip()


def _resolve_presets_path(path):
    """Return the preset file path."""
    if path:
        return PATH(path)
    return PATH(DEFAULT_CODEX_PRESETS_PATH)


def _resolve_codex_config_path(path):
    """Return the user's Codex config.toml path."""
    if path:
        return PATH(path)
    return PATH.home() / ".codex" / "config.toml"


def _resolve_codex_auth_path(path):
    """Return the user's Codex auth.json path."""
    if path:
        return PATH(path)
    return PATH.home() / ".codex" / "auth.json"

