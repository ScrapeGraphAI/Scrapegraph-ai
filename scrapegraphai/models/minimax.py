"""
MiniMax Module
"""

from langchain_openai import ChatOpenAI


DEFAULT_MINIMAX_OPENAI_BASE_URL = "https://api.minimax.io/v1"


class MiniMax(ChatOpenAI):
    """
    A wrapper for the ChatOpenAI class (MiniMax uses an OpenAI-compatible API) that
    provides default configuration and could be extended with additional methods
    if needed.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        if "base_url" not in llm_config and "openai_api_base" not in llm_config:
            llm_config["openai_api_base"] = DEFAULT_MINIMAX_OPENAI_BASE_URL

        super().__init__(**llm_config)
