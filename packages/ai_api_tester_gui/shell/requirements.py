"""GUI 包外依赖收口文件。"""

import json
from pathlib import Path
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from packages.ai_api_tester.shell.exports import (
    create_service as CORE_CREATE_SERVICE,
    get_statistics as CORE_GET_STATISTICS,
    list_models as CORE_LIST_MODELS,
    run_image_chat as CORE_RUN_IMAGE_CHAT,
    run_text_chat as CORE_RUN_TEXT_CHAT,
)


# GUI 层所有包外依赖统一从这里导出。
JSON = json
PATH = Path
THREADING = threading
TK = tk
FILEDIALOG = filedialog
MESSAGEBOX = messagebox
TTK = ttk
SCROLLEDTEXT = ScrolledText
CORE_CREATE_SERVICE = CORE_CREATE_SERVICE
CORE_GET_STATISTICS = CORE_GET_STATISTICS
CORE_LIST_MODELS = CORE_LIST_MODELS
CORE_RUN_IMAGE_CHAT = CORE_RUN_IMAGE_CHAT
CORE_RUN_TEXT_CHAT = CORE_RUN_TEXT_CHAT
