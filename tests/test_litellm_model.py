"""Tests for the LiteLLM model integration."""

import asyncio
import sys
import types
from types import SimpleNamespace
from unittest import mock

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, LLMResult

from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.models import LiteLLM
from scrapegraphai.models.litellm import (
    get_litellm_model_tokens,
    get_litellm_token_costs,
)
from scrapegraphai.utils.custom_callback import CustomCallbackHandler


def _fake_response(content="hello", cost=0.00042):
    response = SimpleNamespace(
        model="claude-sonnet-4-6",
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content), finish_reason="stop"
            )
        ],
        usage=SimpleNamespace(prompt_tokens=12, completion_tokens=3, total_tokens=15),
    )
    response._hidden_params = {"response_cost": cost}
    return response


@pytest.fixture
def fake_litellm(monkeypatch):
    """Install a stub litellm module so the tests run without the extra."""
    module = types.ModuleType("litellm")
    module.completion = mock.MagicMock(return_value=_fake_response())
    module.acompletion = mock.AsyncMock(return_value=_fake_response("async"))
    module.get_model_info = mock.MagicMock(
        return_value={"max_input_tokens": 200000, "max_tokens": 64000}
    )
    module.cost_per_token = mock.MagicMock(return_value=(0.00036, 0.00006))
    monkeypatch.setitem(sys.modules, "litellm", module)
    return module


def test_invoke_calls_litellm_completion(fake_litellm):
    model = LiteLLM(model="anthropic/claude-sonnet-4-6", temperature=0)

    result = model.invoke([SystemMessage("be brief"), HumanMessage("hi")])

    kwargs = fake_litellm.completion.call_args.kwargs
    assert kwargs["model"] == "anthropic/claude-sonnet-4-6"
    assert kwargs["messages"] == [
        {"role": "system", "content": "be brief"},
        {"role": "user", "content": "hi"},
    ]
    assert kwargs["temperature"] == 0
    assert kwargs["drop_params"] is True
    assert result.content == "hello"


def test_unset_credentials_are_not_forwarded(fake_litellm):
    LiteLLM(model="anthropic/claude-sonnet-4-6").invoke("hi")

    kwargs = fake_litellm.completion.call_args.kwargs
    for key in ("api_key", "api_base", "temperature", "max_tokens", "num_retries"):
        assert key not in kwargs
    assert "streaming" not in kwargs


def test_config_is_mapped_to_litellm_arguments(fake_litellm):
    model = LiteLLM(
        model="openai/gpt-4o-mini",
        api_key="sk-test",
        base_url="http://localhost:4000",
        max_tokens=256,
        max_retries=3,
        top_p=0.5,
        streaming=False,
    )

    model.invoke("hi")

    kwargs = fake_litellm.completion.call_args.kwargs
    assert kwargs["api_key"] == "sk-test"
    assert kwargs["api_base"] == "http://localhost:4000"
    assert kwargs["max_tokens"] == 256
    assert kwargs["num_retries"] == 3
    assert kwargs["top_p"] == 0.5
    assert "streaming" not in kwargs


def test_drop_params_can_be_disabled(fake_litellm):
    LiteLLM(model="openai/gpt-4o-mini", drop_params=False).invoke("hi")

    assert fake_litellm.completion.call_args.kwargs["drop_params"] is False


def test_usage_and_cost_are_reported(fake_litellm):
    message = LiteLLM(model="anthropic/claude-sonnet-4-6").invoke("hi")

    assert message.usage_metadata == {
        "input_tokens": 12,
        "output_tokens": 3,
        "total_tokens": 15,
    }
    assert message.response_metadata["response_cost"] == 0.00042
    assert message.response_metadata["prompt_cost"] == 0.00036
    assert message.response_metadata["completion_cost"] == 0.00006
    assert message.response_metadata["finish_reason"] == "stop"
    kwargs = fake_litellm.cost_per_token.call_args.kwargs
    assert kwargs["model"] == "anthropic/claude-sonnet-4-6"
    assert (kwargs["prompt_tokens"], kwargs["completion_tokens"]) == (12, 3)


def test_cost_split_omitted_when_litellm_cannot_price_model(fake_litellm):
    fake_litellm.cost_per_token.side_effect = Exception("not mapped")

    message = LiteLLM(model="openai/my-proxy-alias").invoke("hi")

    assert message.response_metadata["response_cost"] == 0.00042
    assert "prompt_cost" not in message.response_metadata
    assert "completion_cost" not in message.response_metadata


def test_cost_split_omitted_when_it_does_not_match_total(fake_litellm):
    fake_litellm.cost_per_token.return_value = (0.1, 0.2)

    message = LiteLLM(model="anthropic/claude-sonnet-4-6").invoke("hi")

    assert message.response_metadata["response_cost"] == 0.00042
    assert "prompt_cost" not in message.response_metadata


def test_token_costs_split_prompt_and_completion(fake_litellm):
    assert get_litellm_token_costs("anthropic/claude-sonnet-4-6", 12, 3) == (
        0.00036,
        0.00006,
    )


def test_cost_split_failure_keeps_the_completion(fake_litellm):
    fake_litellm.cost_per_token.side_effect = KeyError("boom")

    assert get_litellm_token_costs("anthropic/claude-sonnet-4-6", 12, 3) is None
    message = LiteLLM(model="anthropic/claude-sonnet-4-6").invoke("hi")

    assert message.response_metadata["response_cost"] == 0.00042
    assert "prompt_cost" not in message.response_metadata


def test_ainvoke_calls_litellm_acompletion(fake_litellm):
    model = LiteLLM(model="gemini/gemini-2.5-flash")

    result = asyncio.run(model.ainvoke("hi"))

    assert result.content == "async"
    assert fake_litellm.acompletion.call_args.kwargs["model"] == (
        "gemini/gemini-2.5-flash"
    )
    fake_litellm.completion.assert_not_called()


def test_missing_litellm_raises_install_hint(monkeypatch):
    monkeypatch.setitem(sys.modules, "litellm", None)

    with pytest.raises(ImportError, match=r"scrapegraphai\[litellm\]"):
        LiteLLM(model="openai/gpt-4o-mini").invoke("hi")


def test_model_tokens_come_from_litellm_model_map(fake_litellm):
    assert get_litellm_model_tokens("anthropic/claude-sonnet-4-6") == 200000
    fake_litellm.get_model_info.assert_called_once_with("anthropic/claude-sonnet-4-6")


def test_model_tokens_none_for_unknown_model(fake_litellm):
    fake_litellm.get_model_info.side_effect = Exception("not mapped")

    assert get_litellm_model_tokens("my-proxy-alias") is None


def test_model_tokens_ignore_max_tokens_output_limit(fake_litellm):
    # LiteLLM sets max_tokens to the output limit when it is known.
    fake_litellm.get_model_info.return_value = {
        "max_tokens": 8192,
        "max_output_tokens": 8192,
    }

    assert get_litellm_model_tokens("gemini/gemini-gemma-2-9b-it") is None


def test_model_tokens_reraise_unexpected_errors(fake_litellm):
    fake_litellm.get_model_info.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError):
        get_litellm_model_tokens("anthropic/claude-sonnet-4-6")


def test_model_tokens_none_for_real_litellm_unknown_model():
    pytest.importorskip("litellm")

    assert get_litellm_model_tokens("my-proxy-alias") is None
    assert get_litellm_model_tokens("openai/not-a-real-model") is None


def test_token_costs_with_real_litellm_price_map():
    litellm = pytest.importorskip("litellm")
    model = "anthropic/claude-sonnet-4-6"
    info = litellm.get_model_info(model)

    prompt_cost, completion_cost = get_litellm_token_costs(model, 1000, 100)

    assert prompt_cost == pytest.approx(1000 * info["input_cost_per_token"])
    assert completion_cost == pytest.approx(100 * info["output_cost_per_token"])
    assert get_litellm_token_costs("my-proxy-alias", 1000, 100) is None


def _graph(llm_config):
    return SmartScraperGraph(
        prompt="List the products",
        source="<html><body>products</body></html>",
        config={"llm": llm_config},
    )


def test_graph_routes_litellm_prefix(fake_litellm):
    graph = _graph({"model": "litellm/anthropic/claude-sonnet-4-6", "api_key": "k"})

    assert isinstance(graph.llm_model, LiteLLM)
    assert graph.llm_model.model == "anthropic/claude-sonnet-4-6"
    assert graph.model_token == 200000
    assert graph.model_tokens_defaulted is False


def test_graph_model_tokens_override_litellm_lookup(fake_litellm):
    graph = _graph({"model": "litellm/openai/gpt-4o-mini", "model_tokens": 1234})

    assert graph.model_token == 1234
    fake_litellm.get_model_info.assert_not_called()


def test_graph_falls_back_when_litellm_does_not_know_model(fake_litellm):
    fake_litellm.get_model_info.side_effect = Exception("not mapped")

    graph = _graph({"model": "litellm/my-proxy-alias"})

    assert graph.model_token == 8192
    assert graph.model_tokens_defaulted is True


def test_custom_callback_uses_reported_cost():
    handler = CustomCallbackHandler("anthropic/claude-sonnet-4-6")
    message = AIMessage(
        content="ok",
        usage_metadata={"input_tokens": 12, "output_tokens": 3, "total_tokens": 15},
        response_metadata={"response_cost": 0.00042},
    )

    handler.on_llm_end(LLMResult(generations=[[ChatGeneration(message=message)]]))

    assert handler.total_cost == pytest.approx(0.00042)
    assert handler.total_tokens == 15
    assert handler.successful_requests == 1


def test_custom_callback_uses_reported_cost_split():
    handler = CustomCallbackHandler("anthropic/claude-sonnet-4-6")
    message = AIMessage(
        content="ok",
        usage_metadata={"input_tokens": 12, "output_tokens": 3, "total_tokens": 15},
        response_metadata={
            "response_cost": 0.00042,
            "prompt_cost": 0.00036,
            "completion_cost": 0.00006,
        },
    )

    handler.on_llm_end(LLMResult(generations=[[ChatGeneration(message=message)]]))

    assert handler.total_cost == pytest.approx(0.00042)
    assert handler.prompt_tokens == 12
    assert handler.completion_tokens == 3


def test_custom_callback_end_to_end_with_litellm_model(fake_litellm):
    handler = CustomCallbackHandler("anthropic/claude-sonnet-4-6")

    LiteLLM(model="anthropic/claude-sonnet-4-6").invoke(
        "hi", config={"callbacks": [handler]}
    )

    assert handler.total_cost == pytest.approx(0.00042)
    assert handler.total_tokens == 15
