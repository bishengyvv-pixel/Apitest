# AI API 测试工具

轻量、直接、可落地的 OpenAI 兼容接口测试项目。

适合用来快速验证：

- 接口地址是否可用
- API Key 是否有效
- 模型列表是否正常返回
- 文本与多模态请求是否能稳定跑通

项目当前保留两种使用方式：

- `Web`：本地启动一个简洁的测试页面
- `CLI`：直接用命令行发请求、查模型、看统计

## Preview

![AI API Tester Web Preview](./docs/assets/web-preview.png)

Web 界面预览，建议优先展示左侧导航、测试卡片和响应区域。

## Quick Start

建议全程使用 `uv`。

```bash
uv run python main.py web
```

启动后访问：

```text
http://127.0.0.1:8765
```

如果你更偏向命令行：

```bash
uv run python main.py models --base-url https://api.openai.com/v1 --api-key <YOUR_KEY>
uv run python main.py chat --model gpt-4o-mini --prompt "你好，请介绍一下你自己"
uv run python main.py vision --model gpt-4.1-mini --prompt "请描述这张图片" --image ./demo.png
uv run python main.py stats
```

## Why This Project

- 少填参数：Web 页面只保留连接测试真正需要的信息
- 上手快：开箱即可验证文本、多模态、模型列表
- 结构清晰：项目按分层依赖规范组织，便于继续扩展
- 双模式：适合手动测试，也适合脚本化调用

## Web Mode

Web 页面主要面向“连通性验证”和“快速回归”。

你只需要关注：

- `baseurl`
- `apikey`
- `模型列表`

页面内置了两类测试动作：

- `发送默认文本`：快速验证基础对话接口
- `发送默认图片`：快速验证多模态接口

默认测试图片位于：

`packages/ai_api_tester_web/assets/default-vision.png`

## CLI Commands

```bash
uv run python main.py web
uv run python main.py models
uv run python main.py chat --prompt "hello"
uv run python main.py vision --prompt "describe this image" --image ./demo.png
uv run python main.py stats
```

可配的常用参数：

- `--base-url`
- `--api-key`
- `--model`
- `--timeout`
- `--max-tokens`
- `--system-prompt`
- `--user-agent`
- `--json`

## Environment

- `AI_API_BASE_URL`
- `AI_API_KEY`
- `AI_DEFAULT_MODEL`
- `AI_HISTORY_PATH`
- `AI_TIMEOUT_SECONDS`
- `AI_MAX_TOKENS`
- `AI_SYSTEM_PROMPT`
- `AI_HTTP_USER_AGENT`

## History

成功请求会记录到：

`data/ai_api_tester_history.jsonl`

`stats` 会基于该文件输出：

- 会话总数
- 平均会话时长
- 累计会话时长
- Token 消耗
- 按模型聚合的统计结果

## FAQ

### Web 页面报 `HTTP 403` 或 `browser_signature_banned`

这通常不是本地页面的问题，而是上游接口拒绝了当前请求来源。

优先检查：

1. `baseurl` 是否为供应商正式提供的 API 根地址
2. 同一组参数能否先在 CLI 跑通
3. 是否需要显式传入 `--user-agent`
4. 目标站点是否限制当前出口 IP、客户端签名或访问方式

## Development Notes

- Web 开发模式使用 Vite，并将 `/api/*` 代理到本地 Python 服务
- 生产构建产物输出到 `packages/ai_api_tester_web/assets`
- 设计与分层说明可继续查看 [`docs/README.md`](docs/README.md)
