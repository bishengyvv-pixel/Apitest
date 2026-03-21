"""桥接 GUI 与核心测试能力。"""

from ...shell.requirements import (
    CORE_CREATE_SERVICE,
    CORE_GET_STATISTICS,
    CORE_LIST_MODELS,
    CORE_RUN_IMAGE_CHAT,
    CORE_RUN_TEXT_CHAT,
)


def fetch_model_list(settings):
    """读取模型列表。"""
    service = CORE_CREATE_SERVICE(settings)
    return CORE_LIST_MODELS(service)


def send_text_chat(settings, model, prompt):
    """发起文本对话。"""
    service = CORE_CREATE_SERVICE(settings)
    return CORE_RUN_TEXT_CHAT(service, model, prompt)


def send_vision_chat(settings, model, prompt, image_path, detail):
    """发起图片对话。"""
    service = CORE_CREATE_SERVICE(settings)
    return CORE_RUN_IMAGE_CHAT(service, model, prompt, image_path, detail)


def fetch_history_statistics(settings):
    """读取历史统计。"""
    service = CORE_CREATE_SERVICE(settings)
    return CORE_GET_STATISTICS(service)
