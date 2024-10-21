"""
    __init__.py file for utils folder
"""
from .prettify_exec_info import prettify_exec_info
from .proxy_rotation import Proxy, parse_or_search_proxy, search_proxy_servers
from .save_audio_from_bytes import save_audio_from_bytes
from .sys_dynamic_import import dynamic_import, srcfile_import
from .cleanup_html import cleanup_html, reduce_html
from .logging import *
from .convert_to_md import convert_to_md
from .screenshot_scraping.screenshot_preparation import (take_screenshot,
                                                         select_area_with_opencv,
                                                         select_area_with_ipywidget,
                                                         crop_image)
from .screenshot_scraping.text_detection import detect_text
from .tokenizer import num_tokens_calculus
from .split_text_into_chunks import split_text_into_chunks
from .llm_callback_manager import CustomLLMCallbackManager
from .schema_trasform import transform_schema
from .cleanup_code import extract_code
from .dict_content_compare import are_content_equal
from .code_error_analysis import (syntax_focused_analysis, execution_focused_analysis,
                                  validation_focused_analysis, semantic_focused_analysis)
from .code_error_correction import (syntax_focused_code_generation,
                                    execution_focused_code_generation,
                                    validation_focused_code_generation,
                                    semantic_focused_code_generation)
from .save_code_to_file import save_code_to_file
from .data_export import export_to_json, export_to_csv, export_to_xml
