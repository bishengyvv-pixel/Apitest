"""产品层服务：负责业务编排与统计聚合。"""

from ...adaptor.impl.api_gateway import (
    build_image_messages,
    build_runtime,
    build_text_messages,
    fetch_models,
    send_chat_completion,
)
from ...adaptor.impl.history_store import append_record, read_records
from ...product.config.defaults import (
    DEFAULT_CHAT_KIND,
    DEFAULT_IMAGE_DETAIL,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_VISION_KIND,
)


def create_service(settings=None):
    """创建运行时服务。"""
    if settings is None:
        settings = {}
    if not isinstance(settings, dict):
        raise ValueError("服务配置必须是字典。")
    return build_runtime(settings)


def list_models(service):
    """查询模型列表。"""
    models = fetch_models(service)
    return {
        "base_url": service["base_url"],
        "count": len(models),
        "models": models,
    }


def run_text_chat(service, model, prompt):
    """执行一次基础文本对话并记录历史。"""
    resolved_model = _resolve_model(service, model)
    resolved_prompt = _require_text(prompt, "prompt")
    system_prompt = _resolve_system_prompt(service)
    messages = build_text_messages(system_prompt, resolved_prompt)
    completion = send_chat_completion(service, resolved_model, messages)
    record = _build_record(DEFAULT_CHAT_KIND, resolved_model, resolved_prompt, completion)
    append_record(service, record)
    return record


def run_image_chat(service, model, prompt, image_path, detail=""):
    """执行一次图片多模态对话并记录历史。"""
    resolved_model = _resolve_model(service, model)
    resolved_prompt = _require_text(prompt, "prompt")
    resolved_image_path = _require_text(image_path, "image")
    resolved_detail = detail or DEFAULT_IMAGE_DETAIL
    system_prompt = _resolve_system_prompt(service)
    messages = build_image_messages(
        system_prompt,
        resolved_prompt,
        resolved_image_path,
        resolved_detail,
    )
    completion = send_chat_completion(service, resolved_model, messages)
    record = _build_record(DEFAULT_VISION_KIND, resolved_model, resolved_prompt, completion)
    record["image_path"] = resolved_image_path
    record["image_detail"] = resolved_detail
    append_record(service, record)
    return record


def get_statistics(service):
    """统计历史会话的平均耗时与 token 消耗。"""
    records = read_records(service)
    total_duration = 0.0
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    latest_session_at = ""
    kind_breakdown = {
        DEFAULT_CHAT_KIND: 0,
        DEFAULT_VISION_KIND: 0,
    }
    per_model = {}

    for record in records:
        duration = _to_float(record.get("elapsed_seconds"))
        usage = _normalize_usage(record.get("usage"))
        model = record.get("model") or "unknown"
        kind = record.get("kind") or DEFAULT_CHAT_KIND
        created_at = record.get("created_at") or ""

        total_duration += duration
        prompt_tokens += usage["prompt_tokens"]
        completion_tokens += usage["completion_tokens"]
        total_tokens += usage["total_tokens"]

        if kind not in kind_breakdown:
            kind_breakdown[kind] = 0
        kind_breakdown[kind] += 1

        if created_at > latest_session_at:
            latest_session_at = created_at

        if model not in per_model:
            per_model[model] = {
                "model": model,
                "session_count": 0,
                "total_duration_seconds": 0.0,
                "average_duration_seconds": 0.0,
                "total_tokens": 0,
            }

        per_model_entry = per_model[model]
        per_model_entry["session_count"] += 1
        per_model_entry["total_duration_seconds"] += duration
        per_model_entry["total_tokens"] += usage["total_tokens"]

    per_model_items = []
    for model_name in sorted(per_model):
        entry = per_model[model_name]
        session_count = entry["session_count"]
        if session_count:
            entry["average_duration_seconds"] = round(
                entry["total_duration_seconds"] / session_count,
                3,
            )
        entry["total_duration_seconds"] = round(entry["total_duration_seconds"], 3)
        per_model_items.append(entry)

    session_count = len(records)
    average_duration = 0.0
    if session_count:
        average_duration = round(total_duration / session_count, 3)

    recent_sessions = []
    for record in reversed(records[-20:]):
        usage = _normalize_usage(record.get("usage"))
        recent_sessions.append(
            {
                "created_at": record.get("created_at") or "",
                "kind": record.get("kind") or DEFAULT_CHAT_KIND,
                "model": record.get("model") or "unknown",
                "elapsed_seconds": round(_to_float(record.get("elapsed_seconds")), 3),
                "total_tokens": usage["total_tokens"],
            }
        )

    return {
        "history_path": service["history_path"],
        "session_count": session_count,
        "average_duration_seconds": average_duration,
        "total_duration_seconds": round(total_duration, 3),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "kind_breakdown": kind_breakdown,
        "latest_session_at": latest_session_at,
        "per_model": per_model_items,
        "recent_sessions": recent_sessions,
    }


def _build_record(kind, model, prompt, completion):
    """规范化单次会话记录。"""
    return {
        "kind": kind,
        "model": model,
        "prompt": prompt,
        "response_text": completion["response_text"],
        "elapsed_seconds": completion["elapsed_seconds"],
        "created_at": completion["created_at"],
        "usage": completion["usage"],
    }


def _resolve_model(service, model):
    """优先使用命令行传入的模型名，否则回退到默认模型。"""
    if model and str(model).strip():
        return str(model).strip()

    default_model = service.get("default_model") or ""
    if default_model:
        return str(default_model).strip()
    raise ValueError("未提供模型名称，请通过 --model 或 AI_DEFAULT_MODEL 指定。")


def _resolve_system_prompt(service):
    """优先使用运行时配置的系统提示词。"""
    system_prompt = service.get("system_prompt") or ""
    if system_prompt and str(system_prompt).strip():
        return str(system_prompt).strip()
    return DEFAULT_SYSTEM_PROMPT


def _require_text(value, field_name):
    """校验关键文本输入不能为空。"""
    text = ""
    if value is not None:
        text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} 不能为空。")
    return text


def _normalize_usage(raw_usage):
    """将 usage 字段整理成统一格式。"""
    usage = raw_usage
    if not isinstance(usage, dict):
        usage = {}
    return {
        "prompt_tokens": _to_int(usage.get("prompt_tokens")),
        "completion_tokens": _to_int(usage.get("completion_tokens")),
        "total_tokens": _to_int(usage.get("total_tokens")),
    }


def _to_int(value):
    """安全地将值转为整数。"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _to_float(value):
    """安全地将值转为浮点数。"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0
