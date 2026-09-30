"""API Route OpenAI-compatible chat model wrapper."""

from langchain_openai import ChatOpenAI


class APIRoute(ChatOpenAI):
    """Use API Route models through its fixed OpenAI-compatible endpoint."""

    def __init__(self, **llm_config):
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        llm_config["openai_api_base"] = "https://global.api-route.com/v1"

        super().__init__(**llm_config)
