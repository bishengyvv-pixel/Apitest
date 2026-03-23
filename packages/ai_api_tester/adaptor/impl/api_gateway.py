"""接口网关：负责模型列表、对话请求和图片编码。"""

from ...adaptor.config.defaults import (
    DEFAULT_API_BASE_URL,
    DEFAULT_CHAT_COMPLETIONS_PATH,
    DEFAULT_HISTORY_PATH,
    DEFAULT_HTTP_USER_AGENT,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODELS_PATH,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
)
from ...shell.requirements import BASE64, JSON, OS, PATH, TIME, URL_ERROR, URL_REQUEST


class UpstreamServiceError(RuntimeError):
    """描述上游接口访问失败的统一异常。"""

    def __init__(self, message, status_code=0, diagnostic_code="", details=None):
        super().__init__(message)
        self.status_code = int(status_code or 0)
        self.diagnostic_code = str(diagnostic_code or "").strip()
        self.details = details or {}


def build_runtime(settings):
    """整理配置并生成运行时字典。"""
    env = OS.environ
    base_url = settings.get("base_url") or env.get("AI_API_BASE_URL") or DEFAULT_API_BASE_URL
    api_key = settings.get("api_key") or env.get("AI_API_KEY") or ""
    history_path = settings.get("history_path") or env.get("AI_HISTORY_PATH") or DEFAULT_HISTORY_PATH
    system_prompt = settings.get("system_prompt") or env.get("AI_SYSTEM_PROMPT") or ""
    default_model = settings.get("default_model") or env.get("AI_DEFAULT_MODEL") or ""
    user_agent = settings.get("user_agent") or env.get("AI_HTTP_USER_AGENT") or DEFAULT_HTTP_USER_AGENT

    timeout_value = settings.get("timeout_seconds")
    if not timeout_value:
        timeout_value = env.get("AI_TIMEOUT_SECONDS")

    max_tokens_value = settings.get("max_tokens")
    if not max_tokens_value:
        max_tokens_value = env.get("AI_MAX_TOKENS")

    return {
        "base_url": str(base_url).rstrip("/"),
        "api_key": str(api_key).strip(),
        "history_path": str(history_path).strip(),
        "system_prompt": str(system_prompt).strip(),
        "default_model": str(default_model).strip(),
        "user_agent": str(user_agent).strip() or DEFAULT_HTTP_USER_AGENT,
        "timeout_seconds": _coerce_positive_int(
            timeout_value,
            DEFAULT_REQUEST_TIMEOUT_SECONDS,
        ),
        "max_tokens": _coerce_positive_int(max_tokens_value, DEFAULT_MAX_TOKENS),
    }


def fetch_models(runtime):
    """读取模型列表并返回精简后的字段。"""
    payload = _request_json(runtime, "GET", DEFAULT_MODELS_PATH)
    models = []
    data = payload.get("data")
    if not isinstance(data, list):
        return models

    for item in data:
        if not isinstance(item, dict):
            continue
        model_id = str(item.get("id") or "").strip()
        if not model_id:
            continue
        models.append(
            {
                "id": model_id,
                "object": str(item.get("object") or "").strip(),
                "owned_by": str(item.get("owned_by") or "").strip(),
            }
        )
    return sorted(models, key=lambda model: model["id"])


def build_text_messages(system_prompt, prompt):
    """构造基础文本对话消息体。"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return messages


def build_image_messages(system_prompt, prompt, image_path, detail):
    """构造图片多模态消息体。"""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    image_url = _read_image_as_data_url(image_path)
    messages.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": detail,
                    },
                },
            ],
        }
    )
    return messages


def send_chat_completion(runtime, model, messages):
    """发起一次聊天完成请求并提取常用字段。"""
    started_at = TIME.strftime("%Y-%m-%dT%H:%M:%SZ", TIME.gmtime())
    start = TIME.perf_counter()
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "stream_options": {"include_usage": True},
        "max_tokens": runtime["max_tokens"],
    }
    response_payload = _request_chat_completion(runtime, payload)
    elapsed_seconds = round(TIME.perf_counter() - start, 3)

    return {
        "created_at": started_at,
        "elapsed_seconds": elapsed_seconds,
        "response_text": extract_assistant_text(response_payload),
        "usage": _normalize_usage(response_payload.get("usage")),
        "raw_response": response_payload,
    }


def extract_assistant_text(payload):
    """兼容字符串与多段内容两种响应格式。"""
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        return ""

    message = first_choice.get("message")
    if isinstance(message, dict):
        content = message.get("content")
        return "\n".join(_extract_text_parts(content)).strip()

    fallback_text = first_choice.get("text")
    if isinstance(fallback_text, str):
        return fallback_text.strip()
    return ""


def _request_json(runtime, method, path, payload=None):
    """通过 urllib 发起 HTTP 请求。"""
    url = runtime["base_url"] + path
    body = None
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": runtime["user_agent"],
    }
    if runtime["api_key"]:
        headers["Authorization"] = f"Bearer {runtime['api_key']}"

    if payload is not None:
        body = JSON.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = URL_REQUEST.Request(url=url, data=body, headers=headers, method=method)

    try:
        with URL_REQUEST.urlopen(request, timeout=runtime["timeout_seconds"]) as response:
            raw_body = response.read().decode("utf-8")
            return JSON.loads(raw_body)
    except URL_ERROR.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise _build_upstream_http_error(runtime, error, error_body) from error
    except URL_ERROR.URLError as error:
        raise UpstreamServiceError(
            f"网络请求失败: {error.reason}",
            diagnostic_code="network_request_failed",
            details={"reason": str(error.reason)},
        ) from error


def _request_chat_completion(runtime, payload):
    """???????????? JSON ? SSE ?????"""
    url = runtime["base_url"] + DEFAULT_CHAT_COMPLETIONS_PATH
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": runtime["user_agent"],
    }
    if runtime["api_key"]:
        headers["Authorization"] = f"Bearer {runtime['api_key']}"

    body = JSON.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = URL_REQUEST.Request(url=url, data=body, headers=headers, method="POST")

    try:
        with URL_REQUEST.urlopen(request, timeout=runtime["timeout_seconds"]) as response:
            raw_body = response.read().decode("utf-8", errors="replace")
            content_type = str(response.headers.get("Content-Type") or "").lower()
            if "text/event-stream" in content_type or _looks_like_sse_payload(raw_body):
                return _parse_stream_events(raw_body)
            return JSON.loads(raw_body)
    except URL_ERROR.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        raise _build_upstream_http_error(runtime, error, error_body) from error
    except URL_ERROR.URLError as error:
        raise UpstreamServiceError(
            f"??????: {error.reason}",
            diagnostic_code="network_request_failed",
            details={"reason": str(error.reason)},
        ) from error


def _looks_like_sse_payload(raw_body):
    """??????????????? SSE?"""
    for line in str(raw_body or "").splitlines():
        stripped = line.strip()
        if stripped:
            return stripped.startswith("data:")
    return False


def _parse_stream_events(raw_body):
    """? SSE ????????????????????"""
    text_chunks = []
    usage = {}
    data_lines = []

    def consume_event(lines):
        nonlocal usage
        if not lines:
            return

        data = "\n".join(lines).strip()
        if not data or data == "[DONE]":
            return

        payload = _parse_json_object(data)
        if not payload:
            return

        chunk_usage = payload.get("usage")
        if isinstance(chunk_usage, dict):
            usage = chunk_usage

        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            return

        choice = choices[0]
        if not isinstance(choice, dict):
            return

        delta = choice.get("delta")
        if isinstance(delta, dict):
            text_chunks.extend(_extract_text_parts(delta.get("content")))

        message = choice.get("message")
        if isinstance(message, dict):
            text_chunks.extend(_extract_text_parts(message.get("content")))

        fallback_text = choice.get("text")
        if isinstance(fallback_text, str) and fallback_text:
            text_chunks.append(fallback_text)

    for line in str(raw_body or "").replace("\r\n", "\n").split("\n"):
        stripped = line.strip()
        if not stripped:
            consume_event(data_lines)
            data_lines = []
            continue
        if stripped.startswith("data:"):
            data_lines.append(stripped[5:].lstrip())

    consume_event(data_lines)

    return {
        "choices": [{"message": {"content": "".join(text_chunks)}}],
        "usage": usage,
    }


def _extract_text_parts(content):
    """?????????????"""
    if isinstance(content, str):
        text = content.strip()
        return [text] if text else []

    if not isinstance(content, list):
        return []

    text_chunks = []
    for part in content:
        if not isinstance(part, dict):
            continue
        if part.get("type") != "text":
            continue
        part_text = part.get("text")
        if isinstance(part_text, str) and part_text.strip():
            text_chunks.append(part_text.strip())
    return text_chunks


def _read_image_as_data_url(image_path):
    """读取本地图片并转成 data URL。"""
    path = PATH(image_path)
    if not path.exists():
        raise FileNotFoundError(f"图片不存在: {image_path}")

    mime_type = _guess_mime_type(path.suffix.lower())
    if not mime_type:
        raise ValueError("仅支持 .png / .jpg / .jpeg / .webp 格式的图片。")

    encoded = BASE64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _guess_mime_type(suffix):
    """根据扩展名推断常见图片 MIME。"""
    if suffix == ".png":
        return "image/png"
    if suffix == ".jpg":
        return "image/jpeg"
    if suffix == ".jpeg":
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return ""


def _normalize_usage(raw_usage):
    """兼容 usage 字段缺失的情况。"""
    usage = raw_usage
    if not isinstance(usage, dict):
        usage = {}
    prompt_tokens = _coerce_positive_int(usage.get("prompt_tokens"), 0)
    completion_tokens = _coerce_positive_int(usage.get("completion_tokens"), 0)
    total_tokens = _coerce_positive_int(usage.get("total_tokens"), 0)
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def _build_upstream_http_error(runtime, error, error_body):
    """将 HTTPError 归一化为可诊断的上游异常。"""
    parsed_payload = _parse_json_object(error_body)
    detail = (error_body or "").strip() or str(error.reason)
    host = _extract_host(runtime.get("base_url") or "")

    if _is_cloudflare_browser_ban(parsed_payload):
        zone = str(parsed_payload.get("zone") or host or "").strip()
        message = (
            f"上游接口返回 HTTP {error.code}，Cloudflare 已拒绝当前客户端签名。"
            f"站点 {zone or host or 'unknown'} 标记为 browser_signature_banned / Error 1010，"
            "这通常不是 apikey 错误，而是该接口域名不接受当前这类服务端请求、"
            "需要供应商放行客户端标识或 IP，或该域名本身并非面向通用 OpenAI 兼容 API 调用。"
            "请不要直接重试相同请求，优先确认你填写的是供应商正式支持的 API 域名，"
            "并联系站点方为当前客户端签名放行。"
        )
        return UpstreamServiceError(
            message,
            status_code=error.code,
            diagnostic_code="cloudflare_browser_signature_banned",
            details={
                "status_code": error.code,
                "host": host,
                "zone": zone,
                "error_code": str(parsed_payload.get("error_code") or ""),
                "error_name": str(parsed_payload.get("error_name") or ""),
                "retryable": bool(parsed_payload.get("retryable")),
                "owner_action_required": bool(parsed_payload.get("owner_action_required")),
            },
        )

    return UpstreamServiceError(
        f"上游接口返回 HTTP {error.code}: {detail}",
        status_code=error.code,
        diagnostic_code=f"http_{error.code}",
        details={
            "status_code": error.code,
            "host": host,
            "raw_detail": detail,
        },
    )


def _parse_json_object(raw_text):
    """尽量将错误体解析为 JSON 对象。"""
    try:
        payload = JSON.loads(raw_text)
        if isinstance(payload, dict):
            return payload
    except (TypeError, ValueError):
        return {}
    return {}


def _extract_host(base_url):
    """从 base_url 中提取主机名，便于诊断输出。"""
    text = str(base_url or "").strip()
    if "://" not in text:
        return ""
    without_scheme = text.split("://", 1)[1]
    return without_scheme.split("/", 1)[0].strip()


def _is_cloudflare_browser_ban(payload):
    """识别 Cloudflare 1010 / browser_signature_banned 错误。"""
    if not isinstance(payload, dict):
        return False

    title = str(payload.get("title") or "")
    error_name = str(payload.get("error_name") or "")
    error_code = str(payload.get("error_code") or "")
    detail = str(payload.get("detail") or "")

    indicators = (
        payload.get("cloudflare_error") is True,
        "Error 1010" in title,
        error_name == "browser_signature_banned",
        error_code == "1010",
        "browser's signature" in detail,
    )
    return any(indicators)


def _coerce_positive_int(value, default_value):
    """将配置值收敛成正整数。"""
    try:
        integer_value = int(value)
        if integer_value > 0:
            return integer_value
    except (TypeError, ValueError):
        pass
    return default_value
