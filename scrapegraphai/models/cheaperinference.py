"""
Cheaper Inference Module
"""

from langchain_openai import ChatOpenAI


class CheaperInference(ChatOpenAI):
    """
    A wrapper for ChatOpenAI configured for Cheaper Inference's OpenAI-compatible
    LLM API. Each model costs 15–60% less than the list price of its lab.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        llm_config["openai_api_base"] = "https://api.cheaperinference.com/v1"

        super().__init__(**llm_config)
