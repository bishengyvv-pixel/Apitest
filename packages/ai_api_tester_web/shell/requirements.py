"""Web 包外依赖收口文件。"""

import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from packages.ai_api_tester.shell.exports import (
    create_service as CORE_CREATE_SERVICE,
    list_models as CORE_LIST_MODELS,
    run_image_chat as CORE_RUN_IMAGE_CHAT,
    run_text_chat as CORE_RUN_TEXT_CHAT,
)


# Web 层所有包外依赖统一从这里导出。
JSON = json
MIMETYPES = mimetypes
BASE_HANDLER = BaseHTTPRequestHandler
THREADING_HTTP_SERVER = ThreadingHTTPServer
PATH = Path
URL_PARSE = urlparse
CORE_CREATE_SERVICE = CORE_CREATE_SERVICE
CORE_LIST_MODELS = CORE_LIST_MODELS
CORE_RUN_IMAGE_CHAT = CORE_RUN_IMAGE_CHAT
CORE_RUN_TEXT_CHAT = CORE_RUN_TEXT_CHAT
