"""命令行入口：使用 uv 运行 AI API 接口测试工具。"""

import argparse
import json
import sys

from packages.ai_api_tester.shell.exports import (
    create_service,
    get_statistics,
    list_models,
    run_image_chat,
    run_text_chat,
)


def build_parser():
    """构建命令行参数解析器。"""
    shared_parser = argparse.ArgumentParser(add_help=False)
    add_shared_arguments(shared_parser)

    parser = argparse.ArgumentParser(
        description="一个面向 OpenAI 兼容接口的 AI API 测试工具。",
        parents=[shared_parser],
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("models", help="获取模型列表。", parents=[shared_parser])

    chat_parser = subparsers.add_parser(
        "chat",
        help="发起基础文本对话。",
        parents=[shared_parser],
    )
    chat_parser.add_argument("--model", default="", help="模型名称，未传时读取 AI_DEFAULT_MODEL。")
    chat_parser.add_argument("--prompt", required=True, help="用户输入内容。")

    vision_parser = subparsers.add_parser(
        "vision",
        help="发起图片多模态对话。",
        parents=[shared_parser],
    )
    vision_parser.add_argument("--model", default="", help="模型名称，未传时读取 AI_DEFAULT_MODEL。")
    vision_parser.add_argument("--prompt", required=True, help="结合图片发起的文本问题。")
    vision_parser.add_argument("--image", required=True, help="本地图片路径。")
    vision_parser.add_argument(
        "--detail",
        default="auto",
        choices=["auto", "low", "high"],
        help="图片理解精度参数。",
    )

    subparsers.add_parser("stats", help="查看历史会话统计信息。", parents=[shared_parser])
    subparsers.add_parser(
        "gui",
        help="启动 Web 图形界面。",
        aliases=["web"],
        parents=[shared_parser],
    )
    return parser


def add_shared_arguments(parser):
    """复用共享参数，兼容参数写在子命令前后两种形式。"""
    parser.add_argument(
        "--base-url",
        default="",
        help="接口基础地址，未传时读取 AI_API_BASE_URL，默认回退到 https://api.openai.com/v1",
    )
    parser.add_argument(
        "--api-key",
        default="",
        help="接口密钥，未传时读取 AI_API_KEY。",
    )
    parser.add_argument(
        "--history-path",
        default="",
        help="会话历史文件路径，未传时读取 AI_HISTORY_PATH。",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=0,
        help="接口超时时间（秒），未传时读取 AI_TIMEOUT_SECONDS。",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=0,
        help="单次请求的最大 token 数，未传时读取 AI_MAX_TOKENS。",
    )
    parser.add_argument(
        "--system-prompt",
        default="",
        help="系统提示词，未传时使用内置默认值。",
    )
    parser.add_argument(
        "--user-agent",
        default="",
        help="自定义 HTTP User-Agent，未传时读取 AI_HTTP_USER_AGENT。",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 形式输出结果，便于脚本二次处理。",
    )


def build_settings(args):
    """整理全局配置，交给包内部服务使用。"""
    settings = {}
    if args.base_url:
        settings["base_url"] = args.base_url
    if args.api_key:
        settings["api_key"] = args.api_key
    if args.history_path:
        settings["history_path"] = args.history_path
    if args.timeout:
        settings["timeout_seconds"] = args.timeout
    if args.max_tokens:
        settings["max_tokens"] = args.max_tokens
    if args.system_prompt:
        settings["system_prompt"] = args.system_prompt
    if args.user_agent:
        settings["user_agent"] = args.user_agent
    return settings


def print_json(payload):
    """输出美化后的 JSON。"""
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def print_model_list(payload):
    """格式化打印模型列表。"""
    print(f"接口地址: {payload['base_url']}")
    print(f"模型数量: {payload['count']}")
    if not payload["models"]:
        print("当前未返回可用模型。")
        return

    print("模型列表:")
    for item in payload["models"]:
        owner = item.get("owned_by") or "unknown"
        print(f"- {item['id']} (owned_by={owner})")


def print_chat_result(payload):
    """格式化打印单次会话结果。"""
    usage = payload["usage"]
    print(f"会话类型: {payload['kind']}")
    print(f"模型名称: {payload['model']}")
    print(f"会话时间: {payload['created_at']}")
    print(f"耗时(秒): {payload['elapsed_seconds']}")
    print(
        "Token 使用: "
        f"prompt={usage['prompt_tokens']}, "
        f"completion={usage['completion_tokens']}, "
        f"total={usage['total_tokens']}"
    )
    if payload.get("image_path"):
        print(f"图片路径: {payload['image_path']}")
    print("回复内容:")
    print(payload["response_text"] or "<空回复>")


def print_stats(payload):
    """格式化打印统计信息。"""
    print(f"历史文件: {payload['history_path']}")
    print(f"会话总数: {payload['session_count']}")
    print(f"平均会话时长(秒): {payload['average_duration_seconds']}")
    print(f"累计会话时长(秒): {payload['total_duration_seconds']}")
    print(
        "累计 Token: "
        f"prompt={payload['prompt_tokens']}, "
        f"completion={payload['completion_tokens']}, "
        f"total={payload['total_tokens']}"
    )
    print(
        "会话类型统计: "
        f"文本={payload['kind_breakdown']['chat']}, "
        f"图片={payload['kind_breakdown']['vision']}"
    )
    if payload["latest_session_at"]:
        print(f"最近一次会话时间: {payload['latest_session_at']}")

    if payload["per_model"]:
        print("按模型统计:")
        for item in payload["per_model"]:
            print(
                f"- {item['model']}: "
                f"sessions={item['session_count']}, "
                f"avg_seconds={item['average_duration_seconds']}, "
                f"tokens={item['total_tokens']}"
            )


def main():
    """应用主入口。"""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command in {"gui", "web"}:
            from packages.ai_api_tester_web.shell.exports import launch_web_app

            return launch_web_app(build_settings(args))

        service = create_service(build_settings(args))

        if args.command == "models":
            payload = list_models(service)
        elif args.command == "chat":
            payload = run_text_chat(service, args.model, args.prompt)
        elif args.command == "vision":
            payload = run_image_chat(service, args.model, args.prompt, args.image, args.detail)
        else:
            payload = get_statistics(service)

        if args.json:
            print_json(payload)
        elif args.command == "models":
            print_model_list(payload)
        elif args.command == "stats":
            print_stats(payload)
        else:
            print_chat_result(payload)
        return 0
    except Exception as error:
        print(f"执行失败: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
