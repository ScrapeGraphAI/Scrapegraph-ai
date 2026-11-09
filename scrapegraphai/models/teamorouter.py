"""
TeamoRouter Module
"""

from langchain_openai import ChatOpenAI

TEAMOROUTER_API_BASE = "https://api.teamorouter.com/v1"
TEAMOROUTER_CLIENT_SOURCE = "scrapegraphai-teamorouter"


class TeamoRouter(ChatOpenAI):
    """
    A wrapper for ChatOpenAI configured for TeamoRouter's OpenAI-compatible
    API (https://teamorouter.com), which serves DeepSeek, Qwen, Kimi, GLM and
    other models behind one API key.

    Requests carry an ``X-Client-Source`` header so TeamoRouter can attribute
    traffic to ScrapeGraphAI; headers passed in ``default_headers`` take
    precedence.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "api_key" in llm_config:
            llm_config["openai_api_key"] = llm_config.pop("api_key")
        llm_config["openai_api_base"] = TEAMOROUTER_API_BASE
        llm_config["default_headers"] = {
            "X-Client-Source": TEAMOROUTER_CLIENT_SOURCE,
            **(llm_config.get("default_headers") or {}),
        }

        super().__init__(**llm_config)
