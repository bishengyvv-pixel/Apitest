"""GUI 交互编排层。"""

from ...adaptor.impl.app_bridge import (
    fetch_history_statistics,
    fetch_model_list,
    send_text_chat,
    send_vision_chat,
)
from ...adaptor.impl.config_store import load_saved_settings, save_settings
from ...adaptor.impl.tk_app import DesktopGui
from ...product.config.defaults import DEFAULT_GUI_SETTINGS, GUI_SETTING_KEYS


class GuiPresenter:
    """连接 GUI 界面与核心测试能力。"""

    def __init__(self, initial_settings=None):
        self._initial_settings = merge_settings(initial_settings, load_saved_settings())
        self._ui = DesktopGui()

    def launch(self):
        """启动 GUI 主窗口。"""
        self._ui.set_settings(self._initial_settings)
        self._ui.bind_actions(
            on_save_settings=self._save_settings,
            on_load_models=self._load_models,
            on_send_text=self._send_text_chat,
            on_send_vision=self._send_vision_chat,
            on_refresh_stats=self._refresh_stats,
        )
        self._ui.render_stats(build_stats_view_model(fetch_history_statistics(self._initial_settings)))
        self._ui.run()
        return 0

    def _save_settings(self, form_settings):
        """保存 GUI 当前配置。"""
        settings = extract_service_settings(form_settings)
        save_settings(settings)
        self._ui.set_status("配置已保存。")

    def _load_models(self, form_settings):
        """异步加载模型列表。"""
        settings = extract_service_settings(form_settings)
        self._ui.run_background(
            task=lambda: fetch_model_list(settings),
            on_success=self._handle_models_loaded,
            success_message="模型列表已刷新。",
        )

    def _send_text_chat(self, form_settings, request_payload):
        """异步发起文本对话。"""
        settings = extract_service_settings(form_settings)
        payload = {
            "model": request_payload.get("model") or settings.get("default_model") or "",
            "prompt": request_payload.get("prompt") or "",
        }
        self._ui.run_background(
            task=lambda: self._run_text_request(settings, payload),
            on_success=self._handle_text_chat_finished,
            success_message="文本对话已完成。",
        )

    def _send_vision_chat(self, form_settings, request_payload):
        """异步发起图片对话。"""
        settings = extract_service_settings(form_settings)
        payload = {
            "model": request_payload.get("model") or settings.get("default_model") or "",
            "prompt": request_payload.get("prompt") or "",
            "image_path": request_payload.get("image_path") or "",
            "detail": request_payload.get("detail") or "auto",
        }
        self._ui.run_background(
            task=lambda: self._run_vision_request(settings, payload),
            on_success=self._handle_vision_chat_finished,
            success_message="图片对话已完成。",
        )

    def _refresh_stats(self, form_settings):
        """异步刷新统计数据。"""
        settings = extract_service_settings(form_settings)
        self._ui.run_background(
            task=lambda: fetch_history_statistics(settings),
            on_success=self._handle_stats_loaded,
            success_message="统计信息已刷新。",
        )

    def _run_text_request(self, settings, payload):
        """组合文本对话结果和统计视图。"""
        result = send_text_chat(settings, payload["model"], payload["prompt"])
        stats = fetch_history_statistics(settings)
        return {
            "result": result,
            "stats": stats,
        }

    def _run_vision_request(self, settings, payload):
        """组合图片对话结果和统计视图。"""
        result = send_vision_chat(
            settings,
            payload["model"],
            payload["prompt"],
            payload["image_path"],
            payload["detail"],
        )
        stats = fetch_history_statistics(settings)
        return {
            "result": result,
            "stats": stats,
        }

    def _handle_models_loaded(self, payload):
        """将模型列表渲染到界面。"""
        self._ui.render_models(build_model_view_model(payload))

    def _handle_text_chat_finished(self, payload):
        """更新文本对话和统计视图。"""
        self._ui.render_text_result(payload["result"])
        self._ui.render_stats(build_stats_view_model(payload["stats"]))
        self._ui.apply_model_choices(build_model_choices_from_result(payload["result"]))

    def _handle_vision_chat_finished(self, payload):
        """更新图片对话和统计视图。"""
        self._ui.render_vision_result(payload["result"])
        self._ui.render_stats(build_stats_view_model(payload["stats"]))
        self._ui.apply_model_choices(build_model_choices_from_result(payload["result"]))

    def _handle_stats_loaded(self, payload):
        """将统计结果渲染到界面。"""
        self._ui.render_stats(build_stats_view_model(payload))


def launch_gui(initial_settings=None):
    """对外暴露 GUI 启动入口。"""
    return GuiPresenter(initial_settings).launch()


def merge_settings(cli_settings, saved_settings):
    """合并默认值、已保存配置和命令行传入配置。"""
    merged = {}
    for key in GUI_SETTING_KEYS:
        merged[key] = DEFAULT_GUI_SETTINGS.get(key, "")

    _merge_into(merged, saved_settings)
    _merge_into(merged, cli_settings)
    return merged


def extract_service_settings(form_settings):
    """仅提取核心服务需要的字段。"""
    extracted = {}
    source = form_settings or {}
    for key in GUI_SETTING_KEYS:
        value = source.get(key, "")
        extracted[key] = _to_clean_text(value)
    return extracted


def build_model_view_model(payload):
    """为模型页和下拉选择框生成统一结构。"""
    models = payload.get("models") or []
    rows = []
    choices = []
    for item in models:
        model_id = _to_clean_text(item.get("id"))
        owner = _to_clean_text(item.get("owned_by"))
        if not model_id:
            continue
        choices.append(model_id)
        rows.append(
            {
                "id": model_id,
                "owned_by": owner or "unknown",
                "object": _to_clean_text(item.get("object")),
            }
        )
    return {
        "base_url": _to_clean_text(payload.get("base_url")),
        "count": len(rows),
        "choices": choices,
        "rows": rows,
    }


def build_model_choices_from_result(result):
    """对话后补齐模型选择项，避免手工再次输入。"""
    model_name = _to_clean_text(result.get("model"))
    if not model_name:
        return []
    return [model_name]


def build_stats_view_model(payload):
    """将统计结果整理成界面易渲染的结构。"""
    history_rows = []
    per_model_rows = []

    for item in payload.get("recent_sessions") or []:
        history_rows.append(
            {
                "created_at": _to_clean_text(item.get("created_at")) or "-",
                "kind": _to_clean_text(item.get("kind")) or "chat",
                "model": _to_clean_text(item.get("model")) or "unknown",
                "elapsed_seconds": _to_clean_text(item.get("elapsed_seconds")) or "0",
                "total_tokens": _to_clean_text(item.get("total_tokens")) or "0",
            }
        )

    for item in payload.get("per_model") or []:
        per_model_rows.append(
            {
                "model": _to_clean_text(item.get("model")) or "unknown",
                "session_count": _to_clean_text(item.get("session_count")) or "0",
                "average_duration_seconds": _to_clean_text(item.get("average_duration_seconds")) or "0",
                "total_tokens": _to_clean_text(item.get("total_tokens")) or "0",
            }
        )

    return {
        "history_path": _to_clean_text(payload.get("history_path")),
        "summary": {
            "session_count": _to_clean_text(payload.get("session_count")) or "0",
            "average_duration_seconds": _to_clean_text(payload.get("average_duration_seconds")) or "0",
            "total_tokens": _to_clean_text(payload.get("total_tokens")) or "0",
            "latest_session_at": _to_clean_text(payload.get("latest_session_at")) or "-",
            "prompt_tokens": _to_clean_text(payload.get("prompt_tokens")) or "0",
            "completion_tokens": _to_clean_text(payload.get("completion_tokens")) or "0",
            "chat_count": _to_clean_text((payload.get("kind_breakdown") or {}).get("chat")) or "0",
            "vision_count": _to_clean_text((payload.get("kind_breakdown") or {}).get("vision")) or "0",
        },
        "history_rows": history_rows,
        "per_model_rows": per_model_rows,
    }


def _merge_into(target, source):
    """按字段逐项覆盖。"""
    if not isinstance(source, dict):
        return
    for key in GUI_SETTING_KEYS:
        value = source.get(key)
        if value is None:
            continue
        text = _to_clean_text(value)
        if text != "":
            target[key] = text


def _to_clean_text(value):
    """将界面输入统一成字符串。"""
    if value is None:
        return ""
    return str(value).strip()
