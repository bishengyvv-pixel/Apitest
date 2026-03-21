"""包外依赖收口文件。"""

import base64
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request


# 统一导出包外依赖，避免其他层直接依赖标准库或第三方库。
BASE64 = base64
JSON = json
OS = os
PATH = Path
TIME = time
URL_ERROR = urllib.error
URL_REQUEST = urllib.request
