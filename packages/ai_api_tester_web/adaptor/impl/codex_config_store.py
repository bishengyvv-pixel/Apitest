"""Codex 配置与预设的本地读写。"""

from ...adaptor.config.defaults import DEFAULT_CODEX_PRESETS_PATH
from ...shell.requirements import JSON, PATH


def load_codex_presets(path=None):
    """读取项目内保存的 Codex 预设列表。"""
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
    """保存项目内的 Codex 预设列表。"""
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
    """按名称新增或更新一个 Codex 预设。"""
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
        "message": f"已保存 Codex 预设：{preset['name']}",
    }



def delete_codex_preset(name, path=None):
    """按名称删除一个 Codex 预设。"""
    preset_name = _clean_text(name)
    if not preset_name:
        raise ValueError("预设名称为必填项。")

    presets = load_codex_presets(path)
    remaining_items = [item for item in presets if item["name"] != preset_name]

    if len(remaining_items) == len(presets):
        raise ValueError(f"未找到预设：{preset_name}")

    saved_items = save_codex_presets(remaining_items, path)
    return {
        "deleted_name": preset_name,
        "presets": saved_items,
        "message": f"已删除 Codex 预设：{preset_name}",
    }
def load_codex_active_settings(config_path=None, auth_path=None):
    """读取当前 Codex 生效配置。"""
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
        "api_key": _clean_text(auth_payload.get("OPENAI_API_KEY")),
        "config_path": str(resolved_config_path),
        "auth_path": str(resolved_auth_path),
    }


def apply_codex_preset(payload, presets_path=None, config_path=None, auth_path=None):
    """将预设应用到用户的 Codex 配置。"""
    preset = _normalize_preset(payload, require_all=True)
    upsert_codex_preset(preset, presets_path)

    resolved_config_path = _resolve_codex_config_path(config_path)
    resolved_auth_path = _resolve_codex_auth_path(auth_path)
    _write_codex_config(preset, resolved_config_path)
    _write_codex_auth(preset, resolved_auth_path)

    return {
        "preset": preset,
        "presets": load_codex_presets(presets_path),
        "active": load_codex_active_settings(resolved_config_path, resolved_auth_path),
        "message": f"已将预设 {preset['name']} 应用到 Codex 配置。",
    }


def _write_codex_config(preset, target_path):
    """以最小修改方式更新 Codex config.toml。"""
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
    updated_text = _upsert_root_string(current_text, "model_provider", provider_id)
    updated_text = _upsert_provider_block(updated_text, provider_id, preset["name"], preset["base_url"])
    target_path.write_text(updated_text.rstrip() + "\n", encoding="utf-8")


def _write_codex_auth(preset, target_path):
    """更新 Codex auth.json 中的 OpenAI API Key。"""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _load_json_object(target_path)
    payload["OPENAI_API_KEY"] = preset["api_key"]
    target_path.write_text(JSON.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _upsert_root_string(text, key, value):
    """更新顶层字符串配置，不影响其他段落。"""
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
    """更新或追加指定 provider 的 TOML 段。"""
    header = f"[model_providers.{provider_id}]"
    block_lines = [
        header,
        f'name = "{_escape_toml_string(name)}"',
        f'base_url = "{_escape_toml_string(base_url)}"',
        'wire_api = "responses"',
        "requires_openai_auth = true",
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
    """读取顶层字符串配置。"""
    lines = str(text or "").splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("["):
            break
        if stripped.startswith(f"{key} ="):
            return _parse_toml_string(stripped.split("=", 1)[1])
    return ""


def _read_section(text, section_name):
    """读取指定 TOML 段的原始内容。"""
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
    """读取指定段中的字符串键。"""
    for line in str(section_text or "").splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{key} ="):
            return _parse_toml_string(stripped.split("=", 1)[1])
    return ""


def _parse_toml_string(value):
    """解析最基础的 TOML 字符串。"""
    text = str(value or "").strip()
    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    return text.replace('\\"', '"').replace('\\\\', '\\').strip()


def _escape_toml_string(value):
    """转义写回 TOML 的字符串。"""
    return str(value or "").replace("\\", "\\\\").replace('"', '\\"')


def _load_json_object(path):
    """安全读取 JSON 对象。"""
    if not path.exists():
        return {}
    try:
        payload = JSON.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except (JSON.JSONDecodeError, OSError):
        return {}
    return {}


def _normalize_preset(payload, require_all):
    """统一预设字段结构。"""
    source = payload or {}
    preset = {
        "name": _clean_text(source.get("name")),
        "base_url": _clean_text(source.get("base_url")).rstrip("/"),
        "api_key": _clean_text(source.get("api_key")),
    }
    preset["provider_id"] = _build_provider_id(preset["name"])

    if require_all:
        if not preset["name"]:
            raise ValueError("预设名称为必填项。")
        if not preset["base_url"]:
            raise ValueError("baseurl 为必填项。")
        if not preset["api_key"]:
            raise ValueError("apikey 为必填项。")

    return preset


def _build_provider_id(name):
    """将预设名称转换为稳定的 provider id。"""
    raw_name = _clean_text(name)
    characters = []
    previous_is_dash = False
    for char in raw_name:
        lower_char = char.lower()
        if ("a" <= lower_char <= "z") or ("0" <= lower_char <= "9"):
            characters.append(lower_char)
            previous_is_dash = False
            continue
        if char in "-_ " and not previous_is_dash:
            characters.append("-")
            previous_is_dash = True
            continue
        if ord(char) > 127:
            if characters and not previous_is_dash:
                characters.append("-")
            characters.append(f"u{ord(char):x}")
            previous_is_dash = False

    provider_id = "".join(characters).strip("-")
    if provider_id:
        return f"preset-{provider_id}"
    return "preset-custom"


def _clean_text(value):
    """将任意输入规整为字符串。"""
    if value is None:
        return ""
    return str(value).strip()


def _resolve_presets_path(path):
    """返回预设文件路径。"""
    if path:
        return PATH(path)
    return PATH(DEFAULT_CODEX_PRESETS_PATH)


def _resolve_codex_config_path(path):
    """返回用户 Codex config.toml 路径。"""
    if path:
        return PATH(path)
    return PATH.home() / ".codex" / "config.toml"


def _resolve_codex_auth_path(path):
    """返回用户 Codex auth.json 路径。"""
    if path:
        return PATH(path)
    return PATH.home() / ".codex" / "auth.json"


