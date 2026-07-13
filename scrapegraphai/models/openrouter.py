"""OpenRouter Module"""
from langchain_openai import ChatOpenAI


class OpenRouter(ChatOpenAI):
    """A wrapper for ChatOpenAI configured for OpenRouter's OpenAI-compatible API.

    OpenRouter exposes hundreds of models (OpenAI, Anthropic, Google, Meta,
    DeepSeek, Mistral, Qwen, ...) behind a single OpenAI-compatible endpoint.
    Use it by prefixing the model with ``openrouter/`` in the graph
    configuration, e.g. ``"openrouter/anthropic/claude-3.5-sonnet"``.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        llm_config["openai_api_base"] = "https://openrouter.ai/api/v1"
        super().__init__(**llm_config)
