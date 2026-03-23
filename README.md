# AI API 接口测试工具

这是一个基于 Python 编写的 OpenAI 兼容 API 测试工具，遵循仓库 `docs/` 中的包结构和依赖收口规范实现。

## 功能

- 基础文本对话
- 图片多模态对话
- 模型列表查询
- React Web 图形界面
- 会话平均时长统计
- Token 消耗统计

## 运行方式

建议全程使用 `uv`：

```bash
uv run python main.py gui
uv run python main.py web
uv run python main.py web --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
uv run python main.py models --base-url https://api.openai.com/v1 --api-key <YOUR_KEY>
uv run python main.py chat --model gpt-4o-mini --prompt "你好，请介绍一下你自己"
uv run python main.py vision --model gpt-4.1-mini --prompt "请描述这张图片" --image ./demo.png
uv run python main.py stats
```

## Web GUI 说明

运行 `uv run python main.py gui` 或 `uv run python main.py web` 后，会启动本地 HTTP 服务，默认地址为：

- `http://127.0.0.1:8765`

新的 Web GUI 只要求用户填写：

- `baseurl`：必填
- `apikey`：必填
- `模型列表`：可选，点击“加载模型列表”后可选择

页面不再要求用户手动填写 prompt、上传图片或填写复杂参数，而是直接提供：

- `发送默认文本`：发送内置文本 prompt，用于快速验证基础对话接口
- `发送默认图片`：发送内置测试图片和固定 prompt，用于快速验证多模态接口

默认图片资源位于：

- `packages/ai_api_tester_web/assets/default-vision.png`

## 环境变量

- `AI_API_BASE_URL`: 接口基础地址
- `AI_API_KEY`: API Key
- `AI_DEFAULT_MODEL`: 默认模型名称
- `AI_HISTORY_PATH`: 历史会话文件路径
- `AI_TIMEOUT_SECONDS`: 请求超时时间
- `AI_MAX_TOKENS`: 单次请求最大 token 数
- `AI_SYSTEM_PROMPT`: 默认系统提示词
- `AI_HTTP_USER_AGENT`: 自定义 HTTP `User-Agent`

## 常见故障排查

### Web 中出现 `HTTP 403 / Cloudflare Error 1010 / browser_signature_banned`

这类错误通常表示：

- 被拦截的是你填写的上游接口域名，不是本地 `web` 页面
- 往往不是 `apikey` 错误，而是上游站点把当前客户端签名、IP 或访问方式判定为不允许
- 某些中转站、镜像站或带 Cloudflare 防护的网关并不接受通用服务端 API 调用

建议按下面顺序排查：

1. 确认 `baseurl` 是否是供应商正式文档提供的 API 根地址，而不是站点首页、代理页或临时中转域名
2. 先用命令行测试同一地址，例如 `uv run python main.py models --base-url <BASE_URL> --api-key <KEY>`
3. 如果站点要求客户端标识，启动时显式设置 `AI_HTTP_USER_AGENT` 或传 `--user-agent`
4. 若仍返回 `browser_signature_banned`，不要重复重试，应联系站点方放行当前客户端签名或出口 IP
5. 对 OpenAI 兼容接口，优先使用供应商明确支持的 `/v1` API 域名

## 历史统计

每次成功请求都会记录到 `data/ai_api_tester_history.jsonl`，`stats` 命令会基于该文件计算：

- 会话总数
- 平均会话时长
- 累计会话时长
- prompt / completion / total token
- 按模型维度的会话数与 token 消耗
- 最近 20 次会话摘要

## 说明

当前 Web GUI 的 React、ReactDOM 和 Babel 通过 CDN 加载，因此首次打开页面需要可以访问外网 CDN。

