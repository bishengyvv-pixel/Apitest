"""Web 产品服务：负责 HTTP 路由与页面启动。"""

from ...adaptor.config.defaults import DEFAULT_WEB_HOST, DEFAULT_WEB_PORT
from ...adaptor.impl.http_app import create_http_server
from ...adaptor.impl.http_bridge import fetch_models, get_assets_dir, send_text_request, send_vision_request
from ...product.config.defaults import (
    APP_SUBTITLE,
    APP_TITLE,
    DEFAULT_TEXT_PROMPT,
    DEFAULT_VISION_IMAGE_NAME,
    DEFAULT_VISION_PROMPT,
)


def launch_web_app(settings=None):
    """启动本地 Web 服务。"""
    app_context = build_app_context(settings)
    server = create_http_server(
        app_context["host"],
        app_context["port"],
        app_context["assets_dir"],
        lambda method, path, payload: handle_api_request(method, path, payload, app_context),
    )

    print(f"Web 界面已启动: http://{app_context['host']}:{app_context['port']}")
    print("按 Ctrl+C 可停止服务。")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWeb 服务已停止。")
    finally:
        server.server_close()
    return 0


def build_app_context(settings=None):
    """生成 Web 运行上下文。"""
    source = settings or {}
    return {
        "host": _to_host(source.get("web_host")) or DEFAULT_WEB_HOST,
        "port": _to_port(source.get("web_port")) or DEFAULT_WEB_PORT,
        "assets_dir": get_assets_dir(),
        "default_image_path": get_assets_dir() / DEFAULT_VISION_IMAGE_NAME,
    }


def handle_api_request(method, path, payload, app_context):
    """统一处理 API 路由。"""
    try:
        if method == "GET" and path == "/api/bootstrap":
            return 200, build_bootstrap_payload()
        if method == "POST" and path == "/api/models":
            return 200, build_models_payload(extract_connection_settings(payload))
        if method == "POST" and path == "/api/default-text":
            return 200, run_default_text(payload)
        if method == "POST" and path == "/api/default-vision":
            return 200, run_default_vision(payload, app_context)
        return 404, {"error": "未找到 API 路径。"}
    except ValueError as error:
        return 400, {"error": str(error)}
    except Exception as error:
        return 500, {"error": f"服务执行失败: {error}"}


def build_bootstrap_payload():
    """返回前端启动所需默认信息。"""
    return {
        "title": APP_TITLE,
        "subtitle": APP_SUBTITLE,
        "default_text_prompt": DEFAULT_TEXT_PROMPT,
        "default_vision_prompt": DEFAULT_VISION_PROMPT,
        "default_vision_image_url": f"/assets/{DEFAULT_VISION_IMAGE_NAME}",
    }


def build_models_payload(settings):
    """构造模型列表响应。"""
    payload = fetch_models(settings)
    models = payload.get("models") or []
    selected_model = ""
    if models:
        selected_model = str(models[0].get("id") or "").strip()
    return {
        "models": models,
        "selected_model": selected_model,
    }


def run_default_text(payload):
    """执行默认文本请求。"""
    settings = extract_connection_settings(payload)
    selected_model = resolve_selected_model(settings, payload.get("model"))
    result = send_text_request(settings, selected_model, DEFAULT_TEXT_PROMPT)
    return build_action_payload("text", selected_model, DEFAULT_TEXT_PROMPT, result)


def run_default_vision(payload, app_context):
    """执行默认图片请求。"""
    settings = extract_connection_settings(payload)
    selected_model = resolve_selected_model(settings, payload.get("model"))
    result = send_vision_request(
        settings,
        selected_model,
        DEFAULT_VISION_PROMPT,
        str(app_context["default_image_path"]),
    )
    response_payload = build_action_payload("vision", selected_model, DEFAULT_VISION_PROMPT, result)
    response_payload["default_vision_image_url"] = f"/assets/{DEFAULT_VISION_IMAGE_NAME}"
    return response_payload


def build_action_payload(kind, model, prompt, result):
    """整理前端使用的请求结果。"""
    return {
        "kind": kind,
        "model": model,
        "prompt": prompt,
        "response_text": result.get("response_text") or "",
        "created_at": result.get("created_at") or "",
        "elapsed_seconds": result.get("elapsed_seconds") or 0,
        "usage": result.get("usage") or {},
        "raw": result,
    }


def resolve_selected_model(settings, preferred_model):
    """若前端未选择模型，则自动取模型列表第一项。"""
    preferred_text = _clean_text(preferred_model)
    if preferred_text:
        return preferred_text

    payload = fetch_models(settings)
    for item in payload.get("models") or []:
        model_id = _clean_text(item.get("id"))
        if model_id:
            return model_id
    raise ValueError("未选择模型，且接口未返回任何可用模型。")


def extract_connection_settings(payload):
    """只保留并校验前端允许填写的字段。"""
    source = payload or {}
    base_url = _clean_text(source.get("base_url"))
    api_key = _clean_text(source.get("api_key"))
    if not base_url:
        raise ValueError("baseurl 为必填项。")
    if not api_key:
        raise ValueError("apikey 为必填项。")
    return {
        "base_url": base_url,
        "api_key": api_key,
    }


def _clean_text(value):
    """将输入统一成字符串。"""
    if value is None:
        return ""
    return str(value).strip()


def _to_host(value):
    """规范化 host 配置。"""
    return _clean_text(value)


def _to_port(value):
    """规范化端口配置。"""
    try:
        port = int(value)
        if port > 0:
            return port
    except (TypeError, ValueError):
        return 0
    return 0
