"""Web 适配器默认配置。"""

# 默认监听本机地址，避免将测试工具暴露到局域网。
DEFAULT_WEB_HOST = "127.0.0.1"
DEFAULT_WEB_PORT = 8765

# 静态资源目录固定放在包内 assets 下。
DEFAULT_INDEX_FILE = "index.html"
