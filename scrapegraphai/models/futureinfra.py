"""
FutureInfra Module
"""

from langchain_openai import ChatOpenAI


class FutureInfra(ChatOpenAI):
    """
    A wrapper for ChatOpenAI configured for FutureInfra's OpenAI-compatible
    AI API router. Model ids use the ``provider/model`` format,
    e.g. ``openai/gpt-4o-mini``.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        llm_config["openai_api_base"] = "https://futureinfra.ai/v1/ai"

        super().__init__(**llm_config)
