"""
Atlas Cloud Module
"""

from langchain_openai import ChatOpenAI


class AtlasCloud(ChatOpenAI):
    """
    A wrapper for ChatOpenAI configured for Atlas Cloud's OpenAI-compatible
    LLM API.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        llm_config["openai_api_base"] = "https://api.atlascloud.ai/v1"

        super().__init__(**llm_config)
