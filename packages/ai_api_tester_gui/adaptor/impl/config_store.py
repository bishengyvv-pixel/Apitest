"""GUI 本地配置读写。"""

from ...adaptor.config.defaults import DEFAULT_GUI_CONFIG_PATH
from ...shell.requirements import JSON, PATH


_ALLOWED_KEYS = [
    "base_url",
    "api_key",
    "history_path",
    "timeout_seconds",
    "max_tokens",
    "system_prompt",
    "default_model",
]


def load_saved_settings():
    """读取本地保存配置。"""
    path = PATH(DEFAULT_GUI_CONFIG_PATH)
    if not path.exists():
        return {}

    try:
        return _filter_settings(JSON.loads(path.read_text(encoding="utf-8")))
    except (JSON.JSONDecodeError, OSError):
        return {}


def save_settings(settings):
    """保存本地配置。"""
    path = PATH(DEFAULT_GUI_CONFIG_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _filter_settings(settings)
    path.write_text(JSON.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _filter_settings(settings):
    """只保留允许持久化的字段。"""
    if not isinstance(settings, dict):
        return {}

    filtered = {}
    for key in _ALLOWED_KEYS:
        value = settings.get(key)
        if value is None:
            continue
        filtered[key] = str(value).strip()
    return filtered
