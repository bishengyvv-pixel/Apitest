"""桥接 Web 层与核心测试能力。"""

from ...shell.requirements import (
    CORE_CREATE_SERVICE,
    CORE_LIST_MODELS,
    CORE_RUN_IMAGE_CHAT,
    CORE_RUN_TEXT_CHAT,
    PATH,
)


def fetch_models(settings):
    """读取模型列表。"""
    service = CORE_CREATE_SERVICE(settings)
    return CORE_LIST_MODELS(service)


def send_text_request(settings, model, prompt):
    """发起默认文本对话。"""
    service = CORE_CREATE_SERVICE(settings)
    return CORE_RUN_TEXT_CHAT(service, model, prompt)


def send_vision_request(settings, model, prompt, image_path):
    """发起默认图片对话。"""
    service = CORE_CREATE_SERVICE(settings)
    return CORE_RUN_IMAGE_CHAT(service, model, prompt, image_path, "auto")


def get_assets_dir():
    """返回当前包静态资源目录。"""
    return PATH(__file__).resolve().parents[2] / "assets"
