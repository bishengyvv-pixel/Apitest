"""接口网关：负责模型列表、对话请求和图片编码。"""

from ...adaptor.config.defaults import (
    DEFAULT_API_BASE_URL,
    DEFAULT_CHAT_COMPLETIONS_PATH,
    DEFAULT_HISTORY_PATH,
    DEFAULT_MAX_TOKENS,
    DEFAULT_MODELS_PATH,
    DEFAULT_REQUEST_TIMEOUT_SECONDS,
)
from ...shell.requirements import BASE64, JSON, OS, PATH, TIME, URL_ERROR, URL_REQUEST


def build_runtime(settings):
    """整理配置并生成运行时字典。"""
    env = OS.environ
    base_url = settings.get("base_url") or env.get("AI_API_BASE_URL") or DEFAULT_API_BASE_URL
    api_key = settings.get("api_key") or env.get("AI_API_KEY") or ""
    history_path = settings.get("history_path") or env.get("AI_HISTORY_PATH") or DEFAULT_HISTORY_PATH
    system_prompt = settings.get("system_prompt") or env.get("AI_SYSTEM_PROMPT") or ""
    default_model = settings.get("default_model") or env.get("AI_DEFAULT_MODEL") or ""

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
        "stream": False,
        "max_tokens": runtime["max_tokens"],
    }
    response_payload = _request_json(runtime, "POST", DEFAULT_CHAT_COMPLETIONS_PATH, payload)
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
        if isinstance(content, str):
            return content.strip()
        if isinstance(content, list):
            text_chunks = []
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "text":
                    part_text = part.get("text")
                    if isinstance(part_text, str) and part_text.strip():
                        text_chunks.append(part_text.strip())
            return "\n".join(text_chunks).strip()

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
        detail = error_body.strip() or str(error.reason)
        raise RuntimeError(f"HTTP {error.code}: {detail}") from error
    except URL_ERROR.URLError as error:
        raise RuntimeError(f"网络请求失败: {error.reason}") from error


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


def _coerce_positive_int(value, default_value):
    """将配置值收敛成正整数。"""
    try:
        integer_value = int(value)
        if integer_value > 0:
            return integer_value
    except (TypeError, ValueError):
        pass
    return default_value
