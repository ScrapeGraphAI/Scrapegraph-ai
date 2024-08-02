"""A centralized logging system for any library

source code inspired by https://gist.github.com/DiTo97/9a0377f24236b66134eb96da1ec1693f
"""

import logging
import os
import sys
import threading
from functools import lru_cache
from typing import Optional

_library_name = __name__.split(".", maxsplit=1)[0]

DEFAULT_HANDLER = None
_default_logging_level = logging.WARNING

_semaphore = threading.Lock()


def _get_library_root_logger() -> logging.Logger:
    return logging.getLogger(_library_name)


def _set_library_root_logger() -> None:
    global DEFAULT_HANDLER

    with _semaphore:
        if DEFAULT_HANDLER:
            return

        DEFAULT_HANDLER = logging.StreamHandler()  # sys.stderr as stream

        # https://github.com/pyinstaller/pyinstaller/issues/7334#issuecomment-1357447176
        if sys.stderr is None:
            sys.stderr = open(os.devnull, "w", encoding="utf-8")

        DEFAULT_HANDLER.flush = sys.stderr.flush

        library_root_logger = _get_library_root_logger()
        library_root_logger.addHandler(DEFAULT_HANDLER)
        library_root_logger.setLevel(_default_logging_level)
        library_root_logger.propagate = False


def get_logger(name: Optional[str] = None) -> logging.Logger:
    _set_library_root_logger()
    return logging.getLogger(name or _library_name)


def get_verbosity() -> int:
    _set_library_root_logger()
    return _get_library_root_logger().getEffectiveLevel()


def set_verbosity(verbosity: int) -> None:
    _set_library_root_logger()
    _get_library_root_logger().setLevel(verbosity)


def set_verbosity_debug() -> None:
    set_verbosity(logging.DEBUG)


def set_verbosity_info() -> None:
    set_verbosity(logging.INFO)


def set_verbosity_warning() -> None:
    set_verbosity(logging.WARNING)


def set_verbosity_error() -> None:
    set_verbosity(logging.ERROR)


def set_verbosity_fatal() -> None:
    set_verbosity(logging.FATAL)


def set_handler(handler: logging.Handler) -> None:
    _set_library_root_logger()

    assert handler is not None

    _get_library_root_logger().addHandler(handler)


def setDEFAULT_HANDLER() -> None:
    set_handler(DEFAULT_HANDLER)


def unset_handler(handler: logging.Handler) -> None:
    _set_library_root_logger()

    assert handler is not None

    _get_library_root_logger().removeHandler(handler)


def unsetDEFAULT_HANDLER() -> None:
    unset_handler(DEFAULT_HANDLER)


def set_propagation() -> None:
    _get_library_root_logger().propagate = True


def unset_propagation() -> None:
    _get_library_root_logger().propagate = False


def set_formatting() -> None:
    """sets formatting for all handlers bound to the root logger

    ```
        [levelname|filename|line number] time >> message
    ```
    """
    formatter = logging.Formatter(
        "[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s >> %(message)s"
    )

    for handler in _get_library_root_logger().handlers:
        handler.setFormatter(formatter)


def unset_formatting() -> None:
    for handler in _get_library_root_logger().handlers:
        handler.setFormatter(None)


@lru_cache(None)
def warning_once(self, *args, **kwargs):
    """emits warning logs with the same message only once"""
    self.warning(*args, **kwargs)


logging.Logger.warning_once = warning_once
