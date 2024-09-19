"""
Custom callback for LLM token usage statistics.

This module has been taken and modified from the OpenAI callback manager in langchian-community.
https://github.com/langchain-ai/langchain/blob/master/libs/community/langchain_community/callbacks/openai_info.py
"""
from contextlib import contextmanager
import threading
from typing import Any, Dict, List, Optional
from contextvars import ContextVar

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from langchain_core.tracers.context import register_configure_hook

from .model_costs import MODEL_COST_PER_1K_TOKENS_INPUT, MODEL_COST_PER_1K_TOKENS_OUTPUT


def get_token_cost_for_model(
    model_name: str, num_tokens: int, is_completion: bool = False
) -> float:
    """
    Get the cost in USD for a given model and number of tokens.

    Args:
        model_name: Name of the model
        num_tokens: Number of tokens.
        is_completion: Whether the model is used for completion or not.
            Defaults to False.

    Returns:
        Cost in USD.
    """
    if model_name not in MODEL_COST_PER_1K_TOKENS_INPUT:
        return 0.0
    if is_completion:
        return MODEL_COST_PER_1K_TOKENS_OUTPUT[model_name] * (num_tokens / 1000)
        
    return MODEL_COST_PER_1K_TOKENS_INPUT[model_name] * (num_tokens / 1000)


class CustomCallbackHandler(BaseCallbackHandler):
    """Callback Handler that tracks LLMs info."""

    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0

    def __init__(self, llm_model_name: str) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self.model_name = llm_model_name if llm_model_name else "unknown"

    def __repr__(self) -> str:
        return (
            f"Tokens Used: {self.total_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
            f"Successful Requests: {self.successful_requests}\n"
            f"Total Cost (USD): ${self.total_cost}"
        )

    @property
    def always_verbose(self) -> bool:
        """Whether to call verbose callbacks even if verbose is False."""
        return True

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        pass

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Print out the token."""
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Collect token usage."""
        # Check for usage_metadata (langchain-core >= 0.2.2)
        try:
            generation = response.generations[0][0]
        except IndexError:
            generation = None
        if isinstance(generation, ChatGeneration):
            try:
                message = generation.message
                if isinstance(message, AIMessage):
                    usage_metadata = message.usage_metadata
                else:
                    usage_metadata = None
            except AttributeError:
                usage_metadata = None
        else:
            usage_metadata = None
        if usage_metadata:
            token_usage = {"total_tokens": usage_metadata["total_tokens"]}
            completion_tokens = usage_metadata["output_tokens"]
            prompt_tokens = usage_metadata["input_tokens"]


        else:
            if response.llm_output is None:
                return None

            if "token_usage" not in response.llm_output:
                with self._lock:
                    self.successful_requests += 1
                return None

            # compute tokens and cost for this request
            token_usage = response.llm_output["token_usage"]
            completion_tokens = token_usage.get("completion_tokens", 0)
            prompt_tokens = token_usage.get("prompt_tokens", 0)
        if self.model_name in MODEL_COST_PER_1K_TOKENS_INPUT:
            completion_cost = get_token_cost_for_model(
                self.model_name, completion_tokens, is_completion=True
            )
            prompt_cost = get_token_cost_for_model(self.model_name, prompt_tokens)
        else:
            completion_cost = 0
            prompt_cost = 0

        # update shared state behind lock
        with self._lock:
            self.total_cost += prompt_cost + completion_cost
            self.total_tokens += token_usage.get("total_tokens", 0)
            self.prompt_tokens += prompt_tokens
            self.completion_tokens += completion_tokens
            self.successful_requests += 1

    def __copy__(self) -> "CustomCallbackHandler":
        """Return a copy of the callback handler."""
        return self

    def __deepcopy__(self, memo: Any) -> "CustomCallbackHandler":
        """Return a deep copy of the callback handler."""
        return self


custom_callback: ContextVar[Optional[CustomCallbackHandler]] = ContextVar(
    "custom_callback", default=None
)
register_configure_hook(custom_callback, True)

@contextmanager
def get_custom_callback(llm_model_name: str):
    """
    Function to get custom callback for LLM token usage statistics.
    """
    cb = CustomCallbackHandler(llm_model_name)
    custom_callback.set(cb)
    yield cb
    custom_callback.set(None)