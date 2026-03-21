"""Web 产品默认配置。"""

# 页面引导文案统一放在产品配置层，便于前后端共用。
APP_TITLE = "AI API Web 测试台"
APP_SUBTITLE = "只填写连接信息，即可一键发送内置文本和图片测试请求。"

# 默认文本请求内容，前端只展示不要求用户修改。
DEFAULT_TEXT_PROMPT = "请用三句话介绍你自己，并在最后一行输出 READY，以便我确认文本接口工作正常。"

# 默认图片请求内容，与内置测试图片配套使用。
DEFAULT_VISION_PROMPT = "请描述这张测试图片中的主要颜色和结构，并说明这是否能证明多模态接口已经可用。"

# 前端固定使用的默认图片资源名。
DEFAULT_VISION_IMAGE_NAME = "default-vision.png"
