"""
This module provides a custom callback manager for LLM models.

Classes:
- CustomLLMCallbackManager: Manages exclusive access to callbacks for different types of LLM models.
"""

import threading
from contextlib import contextmanager
from langchain_community.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_bedrock_anthropic_callback
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_aws import ChatBedrock
from .custom_callback import get_custom_callback

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
                if isinstance(llm_model, ChatOpenAI) or isinstance(llm_model, AzureChatOpenAI):
                    with get_openai_callback() as cb:
                        yield cb
                elif isinstance(llm_model, ChatBedrock) and llm_model_name is not None \
                    and "claude" in llm_model_name:
                    with get_bedrock_anthropic_callback() as cb:
                        yield cb
                else:
                    with get_custom_callback(llm_model_name) as cb:
                        yield cb
            finally:
                CustomLLMCallbackManager._lock.release()
        else:
            yield None
