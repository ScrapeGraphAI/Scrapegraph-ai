"""
This module provides a custom callback manager for the LLM models.
"""
import threading
from contextlib import contextmanager
from .custom_callback import get_custom_callback

from langchain_community.callbacks import get_openai_callback
from langchain_community.callbacks.manager import get_bedrock_anthropic_callback
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_aws import ChatBedrock

class CustomLLMCallbackManager:
    _lock = threading.Lock()

    @contextmanager
    def exclusive_get_callback(self, llm_model, llm_model_name):
        if CustomLLMCallbackManager._lock.acquire(blocking=False):
            if isinstance(llm_model, ChatOpenAI) or isinstance(llm_model, AzureChatOpenAI):
                try:
                    with get_openai_callback() as cb:
                        yield cb
                finally:
                    CustomLLMCallbackManager._lock.release()
            elif isinstance(llm_model, ChatBedrock) and llm_model_name is not None and "claude" in llm_model_name:
                try:
                    with get_bedrock_anthropic_callback() as cb:
                        yield cb
                finally:
                    CustomLLMCallbackManager._lock.release()
            else:
                try:
                    with get_custom_callback(llm_model_name) as cb:
                        yield cb
                finally:
                    CustomLLMCallbackManager._lock.release()
        else:
            yield None