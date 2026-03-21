"""历史记录存储：负责会话日志读写。"""

from ...adaptor.config.defaults import DEFAULT_HISTORY_PATH
from ...shell.requirements import JSON, PATH


def append_record(runtime, record):
    """向 JSON Lines 历史文件追加一条记录。"""
    history_path = _resolve_history_path(runtime)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as file:
        file.write(JSON.dumps(record, ensure_ascii=False) + "\n")


def read_records(runtime):
    """读取全部历史记录。"""
    history_path = _resolve_history_path(runtime)
    if not history_path.exists():
        return []

    records = []
    with history_path.open("r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = JSON.loads(line)
            except JSON.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                records.append(payload)
    return records


def _resolve_history_path(runtime):
    """统一解析历史文件路径。"""
    history_path = runtime.get("history_path") or ""
    if history_path:
        return PATH(history_path)
    return PATH(DEFAULT_HISTORY_PATH)
