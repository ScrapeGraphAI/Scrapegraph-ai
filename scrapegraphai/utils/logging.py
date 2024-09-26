"""
A centralized logging system for any library.
This module provides functions to manage logging for a library. It includes
functions to get and set the verbosity level, add and remove handlers, and
control propagation. It also includes a function to set formatting for all
handlers bound to the root logger.
Source code inspired by: https://gist.github.com/DiTo97/9a0377f24236b66134eb96da1ec1693f
"""

import logging
import os
import sys
import threading
from functools import lru_cache
from typing import Optional

_library_name = __name__.split(".", maxsplit=1)[0]

DEFAULT_HANDLER = None
_DEFAULT_LOGGING_LEVEL = logging.WARNING

_semaphore = threading.Lock()

def _get_library_root_logger() -> logging.Logger:
    """
    Get the root logger for the library.

    Returns:
        logging.Logger: The root logger for the library.
    """
    return logging.getLogger(_library_name)

def _set_library_root_logger() -> None:
    """
    Set up the root logger for the library.

    This function sets up the default handler for the root logger, 
    if it has not already been set up.
    It also sets the logging level and propagation for the root logger.
    """
    global DEFAULT_HANDLER

    with _semaphore:
        if DEFAULT_HANDLER:
            return

        DEFAULT_HANDLER = logging.StreamHandler()  # sys.stderr as stream

        if sys.stderr is None:
            sys.stderr = open(os.devnull, "w", encoding="utf-8")

        DEFAULT_HANDLER.flush = sys.stderr.flush

        library_root_logger = _get_library_root_logger()
        library_root_logger.addHandler(DEFAULT_HANDLER)
        library_root_logger.setLevel(_DEFAULT_LOGGING_LEVEL)
        library_root_logger.propagate = False

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the specified name.

    If no name is provided, the root logger for the library is returned.

    Args:
        name (Optional[str]): The name of the logger. 
        If None, the root logger for the library is returned.

    Returns:
        logging.Logger: The logger with the specified name.
    """
    _set_library_root_logger()
    return logging.getLogger(name or _library_name)

def get_verbosity() -> int:
    """
    Get the current verbosity level of the root logger for the library.

    Returns:
        int: The current verbosity level of the root logger for the library.
    """
    _set_library_root_logger()
    return _get_library_root_logger().getEffectiveLevel()

def set_verbosity(verbosity: int) -> None:
    """
    Set the verbosity level of the root logger for the library.

    Args:
        verbosity (int): The verbosity level to set.
    """
    _set_library_root_logger()
    _get_library_root_logger().setLevel(verbosity)

def set_verbosity_debug() -> None:
    """
    Set the verbosity level of the root logger for the library to DEBUG.
    """
    set_verbosity(logging.DEBUG)

def set_verbosity_info() -> None:
    """
    Set the verbosity level of the root logger for the library to INFO.
    """
    set_verbosity(logging.INFO)

def set_verbosity_warning() -> None:
    """
    Set the verbosity level of the root logger for the library to WARNING.
    """
    set_verbosity(logging.WARNING)

def set_verbosity_error() -> None:
    """
    Set the verbosity level of the root logger for the library to ERROR.
    """
    set_verbosity(logging.ERROR)

def set_verbosity_fatal() -> None:
    """
    Set the verbosity level of the root logger for the library to FATAL.
    """
    set_verbosity(logging.FATAL)

def set_handler(handler: logging.Handler) -> None:
    """
    Add a handler to the root logger for the library.

    Args:
        handler (logging.Handler): The handler to add.
    """
    _set_library_root_logger()

    assert handler is not None

    _get_library_root_logger().addHandler(handler)

def setDEFAULT_HANDLER() -> None:
    """
    Add the default handler to the root logger for the library.
    """
    set_handler(DEFAULT_HANDLER)

def unset_handler(handler: logging.Handler) -> None:
    """
    Remove a handler from the root logger for the library.

    Args:
        handler (logging.Handler): The handler to remove.
    """
    _set_library_root_logger()

    assert handler is not None

    _get_library_root_logger().removeHandler(handler)

def unsetDEFAULT_HANDLER() -> None:
    """
    Remove the default handler from the root logger for the library.
    """
    unset_handler(DEFAULT_HANDLER)

def set_propagation() -> None:
    """
    Enable propagation of the root logger for the library.
    """
    _get_library_root_logger().propagate = True

def unset_propagation() -> None:
    """
    Disable propagation of the root logger for the library.
    """
    _get_library_root_logger().propagate = False

def set_formatting() -> None:
    """
    Set formatting for all handlers bound to the root logger for the library.

    The formatting is set to: "[levelname|filename:lineno] time >> message"
    """
    formatter = logging.Formatter(
        "[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s >> %(message)s"
    )

    for handler in _get_library_root_logger().handlers:
        handler.setFormatter(formatter)

def unset_formatting() -> None:
    """
    Remove formatting for all handlers bound to the root logger for the library.
    """
    for handler in _get_library_root_logger().handlers:
        handler.setFormatter(None)

@lru_cache(None)
def warning_once(self, *args, **kwargs):
    """
    Emit a warning log with the same message only once.

    This function is added as a method to the logging.Logger class. 
    It emits a warning log with the same message only once,
    even if it is called multiple times with the same message.

    Args:
        *args: The arguments to pass to the logging.Logger.warning method.
        **kwargs: The keyword arguments to pass to the logging.Logger.warning method.
    """
    self.warning(*args, **kwargs)

logging.Logger.warning_once = warning_once
