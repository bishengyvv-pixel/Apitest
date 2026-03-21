"""适配器默认配置。"""

# 默认按 OpenAI 兼容协议约定接口地址与路径。
DEFAULT_API_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODELS_PATH = "/models"
DEFAULT_CHAT_COMPLETIONS_PATH = "/chat/completions"

# 默认将历史记录落在仓库相对目录，方便排查测试结果。
DEFAULT_HISTORY_PATH = "data/ai_api_tester_history.jsonl"

# 请求级别默认值统一由适配层维护。
DEFAULT_REQUEST_TIMEOUT_SECONDS = 60
DEFAULT_MAX_TOKENS = 1024
