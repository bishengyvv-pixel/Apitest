"""GUI 产品默认配置。"""

# GUI 侧统一管理的配置字段，便于保存和恢复用户输入。
GUI_SETTING_KEYS = [
    "base_url",
    "api_key",
    "history_path",
    "timeout_seconds",
    "max_tokens",
    "system_prompt",
    "default_model",
]

# GUI 初始默认值，优先级低于本地保存配置和命令行入参。
DEFAULT_GUI_SETTINGS = {
    "base_url": "",
    "api_key": "",
    "history_path": "",
    "timeout_seconds": "60",
    "max_tokens": "1024",
    "system_prompt": "",
    "default_model": "",
}
