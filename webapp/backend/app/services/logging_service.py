"""
Structured JSON-lines logging service.

Writes to logs/scrapegraphai.log with automatic rotation at 10MB.
Each entry: {"ts":"ISO8601","level":"INFO","module":"name","message":"...","traceback":"..."}
"""

import datetime
import json
import logging
import traceback as tb_mod
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
_LOG_FILE = _LOG_DIR / "scrapegraphai.log"
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
_LOG_LEVEL = logging.DEBUG

_LOG_DIR.mkdir(parents=True, exist_ok=True)


def _rotate_if_needed() -> None:
    if _LOG_FILE.exists() and _LOG_FILE.stat().st_size > _MAX_BYTES:
        suffix = f".{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d-%H%M%S')}.log"
        backup = _LOG_FILE.with_suffix(suffix)
        _LOG_FILE.rename(backup)


def _write(level: str, module: str, message: str, exc_info: str | None = None) -> None:
    _rotate_if_needed()
    entry = {
        "ts": datetime.datetime.now(datetime.UTC).isoformat(),
        "level": level,
        "module": module,
        "message": message,
    }
    if exc_info:
        entry["traceback"] = exc_info
    with _LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def debug(module: str, message: str) -> None:
    _write("DEBUG", module, message)


def info(module: str, message: str) -> None:
    _write("INFO", module, message)


def warning(module: str, message: str) -> None:
    _write("WARNING", module, message)


def error(module: str, message: str, exc: BaseException | None = None) -> None:
    tb = tb_mod.format_exc() if exc is None else "".join(tb_mod.TracebackException.from_exception(exc).format())
    _write("ERROR", module, message, exc_info=tb)


def critical(module: str, message: str, exc: BaseException | None = None) -> None:
    tb = tb_mod.format_exc() if exc is None else "".join(tb_mod.TracebackException.from_exception(exc).format())
    _write("CRITICAL", module, message, exc_info=tb)


LogLevel = str
LogEntry = dict


def read_logs(
    levels: tuple[str, ...] | None = None,
    limit: int = 100,
    after: str | None = None,
) -> list[LogEntry]:
    if not _LOG_FILE.exists():
        return []
    entries: list[LogEntry] = []
    with _LOG_FILE.open("r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            try:
                entry: LogEntry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if levels and entry.get("level") not in levels:
                continue
            if after and entry.get("ts", "") <= after:
                continue
            entries.append(entry)
    return entries[-limit:]


def clear_logs() -> bool:
    if _LOG_FILE.exists():
        _LOG_FILE.unlink()
        return True
    return False
