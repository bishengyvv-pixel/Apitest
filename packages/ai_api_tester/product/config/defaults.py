"""产品层默认配置。"""

# 默认系统提示词用于基础接口联调，便于快速观察模型响应。
DEFAULT_SYSTEM_PROMPT = "你是一名用于接口联调的 AI 助手，请直接、准确地回答。"

# 业务层统一管理会话类型命名，便于后续统计汇总。
DEFAULT_CHAT_KIND = "chat"
DEFAULT_VISION_KIND = "vision"

# 图片理解细节等级默认走自动策略，兼容更多 OpenAI 风格接口。
DEFAULT_IMAGE_DETAIL = "auto"
