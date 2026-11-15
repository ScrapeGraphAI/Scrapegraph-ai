"""
This module provides a custom callback manager for LLM models.

Classes:
- CustomLLMCallbackManager: Manages exclusive access to callbacks for different types of LLM models.
"""

import threading
from contextlib import contextmanager
from typing import Any, Optional
from urllib.parse import urlparse

from langchain_aws import ChatBedrock
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from .custom_callback import get_custom_callback

# Hosts of OpenAI-compatible APIs, mapped to the provider whose prices apply.
# Any other base URL keeps being priced as OpenAI by model name, as before.
OPENAI_COMPATIBLE_HOSTS = {
    "api.openai.com": "openai",
    "api.deepseek.com": "deepseek",
    "api.x.ai": "xai",
    "openrouter.ai": "openrouter",
    "api.groq.com": "groq",
    "api.together.xyz": "together",
    "api.together.ai": "together",
    "api.fireworks.ai": "fireworks",
    "api.mistral.ai": "mistral",
}

# LangChain integration packages, mapped to the provider they call.
PROVIDER_BY_PACKAGE = {
    "langchain_anthropic": "anthropic",
    "langchain_aws": "bedrock",
    "langchain_google_genai": "google_genai",
    "langchain_google_vertexai": "google_vertexai",
    "langchain_mistralai": "mistralai",
    "langchain_groq": "groq",
    "langchain_fireworks": "fireworks",
    "langchain_together": "together",
    "langchain_xai": "xai",
    "langchain_deepseek": "deepseek",
    "langchain_cohere": "cohere",
}


def get_pricing_provider(llm_model: Any) -> Optional[str]:
    """
    Get the provider whose published prices apply to an LLM model instance.

    Args:
        llm_model: The LLM model instance (e.g., ChatOpenAI, AzureChatOpenAI, ChatBedrock).

    Returns:
        A provider name understood by llm-prices, or None for local or unknown
        providers (for example Ollama), which keep a cost of 0.
    """
    if isinstance(llm_model, AzureChatOpenAI):
        return "azure"
    if isinstance(llm_model, ChatOpenAI):
        host = urlparse(getattr(llm_model, "openai_api_base", None) or "").hostname
        return OPENAI_COMPATIBLE_HOSTS.get(host or "", "openai")
    if isinstance(llm_model, ChatBedrock):
        return "bedrock"
    package = type(llm_model).__module__.split(".", 1)[0]
    return PROVIDER_BY_PACKAGE.get(package)


class CustomLLMCallbackManager:
    """
    CustomLLMCallbackManager class provides a mechanism to acquire a callback for LLM models
    in an exclusive, thread-safe manner.

    Attributes:
    _lock (threading.Lock): Ensures that only one callback can be acquired at a time.

    Methods:
    exclusive_get_callback: A context manager that yields the appropriate callback based on
    the LLM model and its name, ensuring exclusive access to the callback.
    """

    _lock = threading.Lock()

    @contextmanager
    def exclusive_get_callback(self, llm_model, llm_model_name):
        """
        Provides an exclusive callback for the LLM model in a thread-safe manner.

        Args:
            llm_model: The LLM model instance (e.g., ChatOpenAI, AzureChatOpenAI, ChatBedrock).
            llm_model_name (str): The name of the LLM model, used for model-specific callbacks.

        Yields:
            The appropriate callback for the LLM model, or None if the lock is unavailable.
        """
        if CustomLLMCallbackManager._lock.acquire(blocking=False):
            try:
                from ..models.minimax import MiniMax

                if isinstance(llm_model, MiniMax):
                    service_tier = llm_model.service_tier or "standard"
                    with get_custom_callback(
                        llm_model_name, service_tier=service_tier
                    ) as cb:
                        yield cb
                else:
                    with get_custom_callback(
                        llm_model_name, provider=get_pricing_provider(llm_model)
                    ) as cb:
                        yield cb
            finally:
                CustomLLMCallbackManager._lock.release()
        else:
            yield None
