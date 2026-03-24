"""HTTP 运行容器。"""

from ...adaptor.config.defaults import DEFAULT_INDEX_FILE
from ...shell.requirements import BASE_HANDLER, JSON, MIMETYPES, PATH, THREADING_HTTP_SERVER, URL_PARSE


def create_http_server(host, port, assets_dir, api_handler):
    """创建 HTTP 服务实例。"""
    MIMETYPES.add_type("text/css", ".css")
    MIMETYPES.add_type("text/javascript", ".js")
    MIMETYPES.add_type("text/babel", ".jsx")

    resolved_assets_dir = PATH(assets_dir).resolve()

    class WebRequestHandler(BASE_HANDLER):
        """通用请求处理器。"""

        def do_GET(self):
            """处理 GET 请求。"""
            parsed = URL_PARSE(self.path)
            if parsed.path.startswith("/api/"):
                self._handle_api("GET", parsed.path)
                return
            self._serve_static(parsed.path)

        def do_POST(self):
            """处理 POST 请求。"""
            parsed = URL_PARSE(self.path)
            if parsed.path.startswith("/api/"):
                self._handle_api("POST", parsed.path)
                return
            self._write_json(404, {"error": "未找到请求路径。"})

        def do_DELETE(self):
            """处理 DELETE 请求。"""
            parsed = URL_PARSE(self.path)
            if parsed.path.startswith("/api/"):
                self._handle_api("DELETE", parsed.path)
                return
            self._write_json(404, {"error": "未找到请求路径。"})

        def log_message(self, _format, *_args):
            """关闭默认访问日志输出。"""
            return

        def _handle_api(self, method, path):
            """将 API 请求委托给上层回调。"""
            payload = {}
            if method in {"POST", "DELETE"}:
                payload = self._read_json_body()
            status_code, response_payload = api_handler(method, path, payload)
            self._write_json(status_code, response_payload)

        def _read_json_body(self):
            """读取 JSON 请求体。"""
            content_length = int(self.headers.get("Content-Length") or 0)
            if content_length <= 0:
                return {}
            raw_body = self.rfile.read(content_length).decode("utf-8")
            if not raw_body.strip():
                return {}
            return JSON.loads(raw_body)

        def _serve_static(self, path):
            """提供静态资源。"""
            target_file = _resolve_static_file(resolved_assets_dir, path)
            if not target_file or not target_file.exists():
                self._write_json(404, {"error": "静态资源不存在。"})
                return

            mime_type = MIMETYPES.guess_type(str(target_file))[0] or "application/octet-stream"
            if target_file.suffix == ".jsx":
                mime_type = "text/babel"

            body = target_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", f"{mime_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _write_json(self, status_code, payload):
            """输出 JSON 响应。"""
            body = JSON.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return THREADING_HTTP_SERVER((host, port), WebRequestHandler)


def _resolve_static_file(assets_dir, path):
    """将 URL 路径解析为静态资源文件。"""
    normalized_path = path or "/"
    if normalized_path == "/":
        return assets_dir / DEFAULT_INDEX_FILE

    if normalized_path.startswith("/assets/"):
        relative_path = normalized_path[len("/assets/") :]
        candidate = (assets_dir / relative_path).resolve()
        if candidate.is_relative_to(assets_dir):
            return candidate
        return None

    return assets_dir / DEFAULT_INDEX_FILE


