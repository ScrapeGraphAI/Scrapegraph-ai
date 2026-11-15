"""
Custom callback for LLM token usage statistics.

This module started as a modified copy of the OpenAI callback manager in
langchain-community (callbacks/openai_info.py). Models listed in model_costs keep
their local prices; any other model is priced from its provider's published
per-token rates through the llm-prices package.
"""

import threading
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, List, Optional

import llm_prices
from langchain_community.callbacks import bedrock_anthropic_callback, openai_info
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from langchain_core.tracers.context import register_configure_hook

from .model_costs import (
    MODEL_COST_PER_1K_TOKENS_INPUT,
    MODEL_COST_TIERS_PER_1K_TOKENS,
    get_model_cost_per_1k_tokens,
)


def get_token_cost_for_model(
    model_name: str,
    num_tokens: int,
    is_completion: bool = False,
    input_tokens: Optional[int] = None,
    service_tier: str = "standard",
) -> float:
    """
    Get the cost in USD for a given model and number of tokens.

    Args:
        model_name: Name of the model
        num_tokens: Number of tokens.
        is_completion: Whether the model is used for completion or not.
            Defaults to False.
        input_tokens: Number of input tokens used to select a pricing tier.
        service_tier: Provider service tier. Defaults to standard.

    Returns:
        Cost in USD.
    """
    if (
        model_name not in MODEL_COST_PER_1K_TOKENS_INPUT
        and model_name not in MODEL_COST_TIERS_PER_1K_TOKENS
    ):
        return 0.0
    if input_tokens is None:
        if is_completion and model_name in MODEL_COST_TIERS_PER_1K_TOKENS:
            raise ValueError(
                "input_tokens is required for completion costs with tiered pricing"
            )
        input_tokens = num_tokens
    rate = get_model_cost_per_1k_tokens(
        model_name,
        input_tokens,
        is_completion=is_completion,
        service_tier=service_tier,
    )
    return rate * (num_tokens / 1000)


def get_listed_price(
    provider: Optional[str], model_name: Optional[str]
) -> Optional[llm_prices.Price]:
    """
    Get a model's published price from the llm-prices table.

    Args:
        provider: Provider that served the request, for example "openai",
            "azure", "bedrock", "anthropic" or "openrouter".
        model_name: Model id as the provider reports it. Dated snapshots,
            Bedrock ids and "provider/" prefixes are understood.

    Returns:
        The price row, or None when the provider or the model is unknown.
    """
    if not provider or not model_name:
        return None
    return llm_prices.lookup_provider(provider, model_name)


def get_listed_cost(
    price: llm_prices.Price,
    prompt_tokens: int,
    completion_tokens: int,
    cache_read_tokens: int = 0,
    cache_write_5m_tokens: int = 0,
    cache_write_1h_tokens: int = 0,
) -> float:
    """
    Get the cost in USD of one response at a provider's published prices.

    Args:
        price: Price row from get_listed_price.
        prompt_tokens: Prompt tokens as LangChain reports them, cache reads
            and cache writes included.
        completion_tokens: Completion tokens, reasoning tokens included.
        cache_read_tokens: Prompt tokens served from the prompt cache.
        cache_write_5m_tokens: Prompt tokens written to a 5-minute cache.
        cache_write_1h_tokens: Prompt tokens written to a 1-hour cache.

    Returns:
        Cost in USD, or 0.0 when a price it needs is not published.
    """
    prompt_tokens = max(0, prompt_tokens)
    cache_read = max(0, min(cache_read_tokens, prompt_tokens))
    cache_write_1h = max(0, min(cache_write_1h_tokens, prompt_tokens - cache_read))
    cache_write_5m = max(
        0, min(cache_write_5m_tokens, prompt_tokens - cache_read - cache_write_1h)
    )
    usage = llm_prices.Usage(
        input=prompt_tokens - cache_read - cache_write_5m - cache_write_1h,
        output=max(0, completion_tokens),
        cache_read=cache_read,
        cache_write_5m=cache_write_5m,
        cache_write_1h=cache_write_1h,
    )
    breakdown = price.cost_usage(usage)
    if breakdown is not None:
        return breakdown.total
    cost = price.cost(prompt_tokens, max(0, completion_tokens))
    return 0.0 if cost is None else cost


def get_legacy_cost(
    provider: Optional[str],
    model_name: Optional[str],
    prompt_tokens: int,
    completion_tokens: int,
    cache_read_tokens: int = 0,
) -> Optional[float]:
    """
    Get the cost in USD from langchain-community's OpenAI and Bedrock Claude
    tables, for retired models (gpt-4-32k, claude-v2, ...) that providers no
    longer list. Those tables are no longer updated, so they are only used
    when llm-prices has no row for the model.

    Returns:
        Cost in USD, or None when the model is not in those tables either.
    """
    if not model_name:
        return None
    try:
        if provider in ("openai", "azure"):
            name = openai_info.standardize_model_name(model_name)
            if name not in openai_info.MODEL_COST_PER_1K_TOKENS:
                return None
            token_type = openai_info.TokenType
            cached = max(0, min(cache_read_tokens, prompt_tokens))
            try:
                cached_cost = openai_info.get_openai_token_cost_for_model(
                    name, cached, token_type=token_type.PROMPT_CACHED
                )
            except ValueError:
                cached_cost = openai_info.get_openai_token_cost_for_model(
                    name, cached, token_type=token_type.PROMPT
                )
            return (
                openai_info.get_openai_token_cost_for_model(
                    name, prompt_tokens - cached, token_type=token_type.PROMPT
                )
                + cached_cost
                + openai_info.get_openai_token_cost_for_model(
                    name, completion_tokens, token_type=token_type.COMPLETION
                )
            )
        if provider == "bedrock":
            base_id = ".".join(model_name.split(".")[-2:])
            input_rates = bedrock_anthropic_callback.MODEL_COST_PER_1K_INPUT_TOKENS
            output_rates = bedrock_anthropic_callback.MODEL_COST_PER_1K_OUTPUT_TOKENS
            if base_id not in input_rates:
                return None
            return (prompt_tokens / 1000) * input_rates[base_id] + (
                completion_tokens / 1000
            ) * output_rates[base_id]
    except ValueError:
        return None
    return None


class CustomCallbackHandler(BaseCallbackHandler):
    """Callback Handler that tracks LLMs info."""

    total_tokens: int = 0
    prompt_tokens: int = 0
    prompt_tokens_cached: int = 0
    completion_tokens: int = 0
    reasoning_tokens: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0

    def __init__(
        self,
        llm_model_name: str,
        service_tier: str = "standard",
        provider: Optional[str] = None,
    ) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self.model_name = llm_model_name if llm_model_name else "unknown"
        self.service_tier = service_tier
        self.provider = provider

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
        response_metadata: Dict[str, Any] = {}
        if isinstance(generation, ChatGeneration):
            try:
                message = generation.message
                if isinstance(message, AIMessage):
                    usage_metadata = message.usage_metadata
                    response_metadata = message.response_metadata or {}
                else:
                    usage_metadata = None
            except AttributeError:
                usage_metadata = None
        else:
            usage_metadata = None
        cache_read_tokens = 0
        cache_write_5m_tokens = 0
        cache_write_1h_tokens = 0
        reasoning_tokens = 0
        if usage_metadata:
            token_usage = {"total_tokens": usage_metadata["total_tokens"]}
            completion_tokens = usage_metadata["output_tokens"]
            prompt_tokens = usage_metadata["input_tokens"]
            input_details: Dict[str, Any] = dict(
                usage_metadata.get("input_token_details") or {}
            )
            output_details: Dict[str, Any] = dict(
                usage_metadata.get("output_token_details") or {}
            )
            cache_read_tokens = input_details.get("cache_read") or 0
            cache_write_1h_tokens = input_details.get("ephemeral_1h_input_tokens") or 0
            cache_write_5m_tokens = input_details.get("ephemeral_5m_input_tokens") or (
                (input_details.get("cache_creation") or 0) - cache_write_1h_tokens
            )
            reasoning_tokens = output_details.get("reasoning") or 0

        else:
            if response.llm_output is None:
                return None

            # Bedrock reports its counts under "usage" instead of "token_usage".
            token_usage = (
                response.llm_output.get("token_usage")
                or response.llm_output.get("usage")
                or {}
            )
            if not token_usage:
                with self._lock:
                    self.successful_requests += 1
                return None

            # compute tokens and cost for this request
            completion_tokens = token_usage.get("completion_tokens", 0)
            prompt_tokens = token_usage.get("prompt_tokens", 0)
        if (
            self.model_name in MODEL_COST_PER_1K_TOKENS_INPUT
            or self.model_name in MODEL_COST_TIERS_PER_1K_TOKENS
        ):
            completion_cost = get_token_cost_for_model(
                self.model_name,
                completion_tokens,
                is_completion=True,
                input_tokens=prompt_tokens,
                service_tier=self.service_tier,
            )
            prompt_cost = get_token_cost_for_model(
                self.model_name,
                prompt_tokens,
                input_tokens=prompt_tokens,
                service_tier=self.service_tier,
            )
        else:
            # The served id (e.g. "gpt-4o-2024-08-06") first, then the configured one.
            llm_output = response.llm_output or {}
            served_model = (
                response_metadata.get("model_name")
                or response_metadata.get("model_id")
                or llm_output.get("model_name")
                or llm_output.get("model_id")
            )
            completion_cost = 0
            prompt_cost = self._provider_cost(
                [served_model, self.model_name],
                prompt_tokens,
                completion_tokens,
                cache_read_tokens,
                cache_write_5m_tokens,
                cache_write_1h_tokens,
            )

        # update shared state behind lock
        with self._lock:
            self.total_cost += prompt_cost + completion_cost
            self.total_tokens += token_usage.get("total_tokens", 0)
            self.prompt_tokens += prompt_tokens
            self.prompt_tokens_cached += cache_read_tokens
            self.completion_tokens += completion_tokens
            self.reasoning_tokens += reasoning_tokens
            self.successful_requests += 1

    def _provider_cost(
        self,
        model_names: List[Optional[str]],
        prompt_tokens: int,
        completion_tokens: int,
        cache_read_tokens: int,
        cache_write_5m_tokens: int,
        cache_write_1h_tokens: int,
    ) -> float:
        """Cost of one response at the provider's prices, 0.0 when unknown."""
        for model_name in model_names:
            price = get_listed_price(self.provider, model_name)
            if price is not None:
                return get_listed_cost(
                    price,
                    prompt_tokens,
                    completion_tokens,
                    cache_read_tokens=cache_read_tokens,
                    cache_write_5m_tokens=cache_write_5m_tokens,
                    cache_write_1h_tokens=cache_write_1h_tokens,
                )
        for model_name in model_names:
            cost = get_legacy_cost(
                self.provider,
                model_name,
                prompt_tokens,
                completion_tokens,
                cache_read_tokens=cache_read_tokens,
            )
            if cost is not None:
                return cost
        return 0.0

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
def get_custom_callback(
    llm_model_name: str,
    service_tier: str = "standard",
    provider: Optional[str] = None,
):
    """
    Function to get custom callback for LLM token usage statistics.

    Args:
        llm_model_name: Name of the model, used to look up its prices.
        service_tier: Provider service tier, for tiered local prices.
        provider: Provider that serves the model. When set, models missing
            from the local price table are priced from llm-prices.
    """
    cb = CustomCallbackHandler(
        llm_model_name, service_tier=service_tier, provider=provider
    )
    custom_callback.set(cb)
    yield cb
    custom_callback.set(None)
