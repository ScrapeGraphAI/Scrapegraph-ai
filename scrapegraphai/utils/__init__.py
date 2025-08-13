"""
__init__.py file for utils folder
"""

from .cleanup_code import extract_code
from .cleanup_html import cleanup_html, reduce_html
from .code_error_analysis import (
    execution_focused_analysis,
    semantic_focused_analysis,
    syntax_focused_analysis,
    validation_focused_analysis,
)
from .code_error_correction import (
    execution_focused_code_generation,
    semantic_focused_code_generation,
    syntax_focused_code_generation,
    validation_focused_code_generation,
)
from .convert_to_md import convert_to_md
from .data_export import export_to_csv, export_to_json, export_to_xml
from .dict_content_compare import are_content_equal
from .llm_callback_manager import CustomLLMCallbackManager
from .logging import (
    get_logger,
    get_verbosity,
    set_formatting,
    set_handler,
    set_propagation,
    set_verbosity,
    set_verbosity_debug,
    set_verbosity_error,
    set_verbosity_fatal,
    set_verbosity_info,
    set_verbosity_warning,
    setDEFAULT_HANDLER,
    unset_formatting,
    unset_handler,
    unset_propagation,
    unsetDEFAULT_HANDLER,
    warning_once,
)
from .prettify_exec_info import prettify_exec_info
from .proxy_rotation import Proxy, parse_or_search_proxy, search_proxy_servers
from .save_audio_from_bytes import save_audio_from_bytes
from .save_code_to_file import save_code_to_file
from .schema_trasform import transform_schema  # Note: filename has typo but kept for compatibility
from .screenshot_scraping.screenshot_preparation import (
    crop_image,
    select_area_with_ipywidget,
    select_area_with_opencv,
    take_screenshot,
)
from .screenshot_scraping.text_detection import detect_text
from .split_text_into_chunks import split_text_into_chunks
from .sys_dynamic_import import dynamic_import, srcfile_import
from .tokenizer import num_tokens_calculus

__all__ = [
    # Code cleanup and analysis
    "extract_code",
    "cleanup_html",
    "reduce_html",
    # Error analysis functions
    "execution_focused_analysis",
    "semantic_focused_analysis",
    "syntax_focused_analysis",
    "validation_focused_analysis",
    # Error correction functions
    "execution_focused_code_generation",
    "semantic_focused_code_generation",
    "syntax_focused_code_generation",
    "validation_focused_code_generation",
    # File and data handling
    "convert_to_md",
    "export_to_csv",
    "export_to_json",
    "export_to_xml",
    "save_audio_from_bytes",
    "save_code_to_file",
    # Utility functions
    "are_content_equal",
    "CustomLLMCallbackManager",
    "prettify_exec_info",
    "transform_schema",
    "split_text_into_chunks",
    "dynamic_import",
    "srcfile_import",
    "num_tokens_calculus",
    # Proxy handling
    "Proxy",
    "parse_or_search_proxy",
    "search_proxy_servers",
    # Screenshot and image processing
    "crop_image",
    "select_area_with_ipywidget",
    "select_area_with_opencv",
    "take_screenshot",
    "detect_text",
    # Logging functions
    "get_logger",
    "get_verbosity",
    "set_verbosity",
    "set_verbosity_debug",
    "set_verbosity_info",
    "set_verbosity_warning",
    "set_verbosity_error",
    "set_verbosity_fatal",
    "set_handler",
    "unset_handler",
    "setDEFAULT_HANDLER",
    "unsetDEFAULT_HANDLER",
    "set_propagation",
    "unset_propagation",
    "set_formatting",
    "unset_formatting",
    "warning_once",
]
