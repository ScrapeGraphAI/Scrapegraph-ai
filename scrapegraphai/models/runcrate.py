"""
Runcrate Module
"""

from langchain_openai import ChatOpenAI


class Runcrate(ChatOpenAI):
    """
    A wrapper for ChatOpenAI configured for Runcrate's OpenAI-compatible
    inference API. Model ids keep their vendor prefix, for example
    ``deepseek-ai/DeepSeek-V4.1-Flash``.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        llm_config["openai_api_base"] = "https://api.runcrate.ai/v1"

        super().__init__(**llm_config)
