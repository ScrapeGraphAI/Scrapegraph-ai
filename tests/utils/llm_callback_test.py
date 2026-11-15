"""Tests for LLM cost tracking in CustomLLMCallbackManager and CustomCallbackHandler."""

import llm_prices
import pytest
from langchain_aws import ChatBedrock
from langchain_community.callbacks.bedrock_anthropic_callback import (
    BedrockAnthropicTokenUsageCallbackHandler,
)
from langchain_community.callbacks.openai_info import OpenAICallbackHandler
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI, ChatOpenAI

from scrapegraphai.models.deepseek import DeepSeek
from scrapegraphai.models.minimax import MiniMax
from scrapegraphai.models.xai import XAI
from scrapegraphai.utils.custom_callback import CustomCallbackHandler
from scrapegraphai.utils.llm_callback_manager import (
    CustomLLMCallbackManager,
    get_pricing_provider,
)


def chat_result(model_name, input_tokens, output_tokens, cache_read=0):
    """An LLMResult shaped like a LangChain chat model response."""
    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
    }
    if cache_read:
        usage["input_token_details"] = {"cache_read": cache_read}
    message = AIMessage(
        content="{}",
        usage_metadata=usage,
        response_metadata={"model_name": model_name},
    )
    return LLMResult(generations=[[ChatGeneration(message=message)]])


def tracked_cost(llm_model, model_name, response):
    """Total cost the graph would report for one response."""
    with CustomLLMCallbackManager().exclusive_get_callback(
        llm_model, model_name
    ) as callback:
        callback.on_llm_end(response)
        return callback


def test_pricing_provider_for_each_client():
    assert get_pricing_provider(ChatOpenAI(model="gpt-5.5", api_key="k")) == "openai"
    assert (
        get_pricing_provider(
            ChatOpenAI(
                model="openai/gpt-4.1",
                api_key="k",
                base_url="https://openrouter.ai/api/v1",
            )
        )
        == "openrouter"
    )
    assert (
        get_pricing_provider(
            ChatOpenAI(model="gpt-4o", api_key="k", base_url="http://localhost:4000")
        )
        == "openai"
    )
    assert (
        get_pricing_provider(
            AzureChatOpenAI(
                azure_deployment="gpt-4o",
                api_key="k",
                api_version="2024-10-21",
                azure_endpoint="https://example.openai.azure.com",
            )
        )
        == "azure"
    )
    assert get_pricing_provider(DeepSeek(model="deepseek-chat", api_key="k")) == (
        "deepseek"
    )
    assert get_pricing_provider(XAI(model="grok-4", api_key="k")) == "xai"
    assert (
        get_pricing_provider(
            ChatBedrock(
                model_id="us.anthropic.claude-sonnet-4-5-20250929-v1:0",
                region_name="us-east-1",
            )
        )
        == "bedrock"
    )
    assert get_pricing_provider(ChatOllama(model="llama3.1")) is None


def test_openai_model_newer_than_langchain_community_table_is_priced():
    """gpt-5.5 is missing from langchain-community's frozen table, which reports $0."""
    response = chat_result("gpt-5.5", 10_000, 2_000)

    frozen = OpenAICallbackHandler()
    frozen.on_llm_end(response)
    assert frozen.total_cost == 0

    callback = tracked_cost(
        ChatOpenAI(model="gpt-5.5", api_key="k"), "gpt-5.5", response
    )
    expected = llm_prices.lookup_provider("openai", "gpt-5.5").cost(10_000, 2_000)
    assert expected > 0
    assert callback.total_cost == pytest.approx(expected)
    assert callback.prompt_tokens == 10_000
    assert callback.completion_tokens == 2_000


def test_openrouter_prefixed_model_is_priced():
    """An OpenRouter id such as openai/gpt-4.1 used to report $0 (issue #1007)."""
    llm = ChatOpenAI(
        model="openai/gpt-4.1", api_key="k", base_url="https://openrouter.ai/api/v1"
    )
    callback = tracked_cost(
        llm, "openai/gpt-4.1", chat_result("openai/gpt-4.1", 193, 20)
    )
    assert callback.total_cost == pytest.approx((193 * 2.0 + 20 * 8.0) / 1e6)


def test_cached_prompt_tokens_bill_at_cache_rate():
    callback = tracked_cost(
        ChatOpenAI(model="gpt-4o-mini", api_key="k"),
        "gpt-4o-mini",
        chat_result("gpt-4o-mini-2024-07-18", 10_000, 1_000, cache_read=8_000),
    )
    expected = (2_000 * 0.15 + 8_000 * 0.075 + 1_000 * 0.6) / 1e6
    assert callback.total_cost == pytest.approx(expected)
    assert callback.prompt_tokens_cached == 8_000


def test_bedrock_claude_newer_than_langchain_community_table_is_priced():
    """The langchain-community Bedrock callback raises for Claude Sonnet 4.5."""
    model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    legacy_response = LLMResult(
        generations=[[]],
        llm_output={
            "usage": {
                "prompt_tokens": 1_000,
                "completion_tokens": 100,
                "total_tokens": 1_100,
            },
            "model_id": model_id,
        },
    )
    with pytest.raises(ValueError, match="Unknown model"):
        BedrockAnthropicTokenUsageCallbackHandler().on_llm_end(legacy_response)

    llm = ChatBedrock(model_id=model_id, region_name="us-east-1")
    callback = tracked_cost(llm, model_id, legacy_response)
    assert callback.total_cost == pytest.approx((1_000 * 3.0 + 100 * 15.0) / 1e6)
    assert callback.prompt_tokens == 1_000


def test_retired_openai_model_keeps_its_previous_price():
    """Models no longer listed by OpenAI fall back to the old table, not to $0."""
    response = chat_result("gpt-4-32k", 1_000, 100)
    frozen = OpenAICallbackHandler()
    frozen.on_llm_end(response)

    callback = tracked_cost(
        ChatOpenAI(model="gpt-4-32k", api_key="k"), "gpt-4-32k", response
    )
    assert frozen.total_cost > 0
    assert callback.total_cost == pytest.approx(frozen.total_cost)


def test_local_price_table_still_wins():
    """Models in model_costs.py keep their local prices."""
    callback = CustomCallbackHandler(
        "meta.llama3-70b-instruct-v1:0", provider="bedrock"
    )
    callback.on_llm_end(chat_result("meta.llama3-70b-instruct-v1:0", 1_000, 1_000))
    assert callback.total_cost == pytest.approx(0.00265 + 0.0035)


def test_minimax_keeps_tiered_callback():
    llm = MiniMax(model="MiniMax-M3", api_key="k", service_tier="priority")
    with CustomLLMCallbackManager().exclusive_get_callback(
        llm, "MiniMax-M3"
    ) as callback:
        assert callback.service_tier == "priority"
        assert callback.provider is None


def test_local_models_cost_nothing():
    callback = tracked_cost(
        ChatOllama(model="llama3.1"), "llama3.1", chat_result("llama3.1", 1_000, 100)
    )
    assert callback.total_cost == 0
    assert callback.total_tokens == 1_100
