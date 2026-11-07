"""
CloudGPU Module
"""

from langchain_openai import ChatOpenAI

DEFAULT_CLOUDGPU_BASE_URL = "https://cloudgpu.app/v1"


class CloudGPU(ChatOpenAI):
    """
    A wrapper for ChatOpenAI configured for CloudGPU's OpenAI-compatible
    model API. Model ids are unprefixed, for example ``deepseek-v4-flash``;
    ``GET https://cloudgpu.app/v1/models`` lists them.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        if "base_url" not in llm_config and "openai_api_base" not in llm_config:
            llm_config["openai_api_base"] = DEFAULT_CLOUDGPU_BASE_URL

        super().__init__(**llm_config)
