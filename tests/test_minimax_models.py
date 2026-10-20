"""Tests for MiniMax model configuration."""

import importlib.util
import json
import os
import sys
import types

import httpx
import pytest


@pytest.fixture(scope="module")
def models_tokens():
    """Import models_tokens directly to avoid triggering the full package init."""
    spec = importlib.util.spec_from_file_location(
        "models_tokens",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "scrapegraphai",
            "helpers",
            "models_tokens.py",
        ),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.models_tokens


@pytest.fixture(scope="module")
def model_costs():
    """Import model_costs directly to avoid triggering the full package init."""
    spec = importlib.util.spec_from_file_location(
        "model_costs",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "scrapegraphai",
            "utils",
            "model_costs.py",
        ),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def minimax_module():
    """Import the MiniMax adapter without loading the package initializer."""
    spec = importlib.util.spec_from_file_location(
        "minimax",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "scrapegraphai",
            "models",
            "minimax.py",
        ),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def custom_callback_module(model_costs):
    """Import custom_callback with its local model_costs dependency."""
    package_name = "_minimax_test_utils"
    package = types.ModuleType(package_name)
    package.__path__ = []
    sys.modules[package_name] = package
    sys.modules[f"{package_name}.model_costs"] = model_costs
    spec = importlib.util.spec_from_file_location(
        f"{package_name}.custom_callback",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "scrapegraphai",
            "utils",
            "custom_callback.py",
        ),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_minimax_m3_in_model_list(models_tokens):
    """MiniMax-M3 should be in the model list."""
    minimax_models = models_tokens["minimax"]
    assert "MiniMax-M3" in minimax_models


def test_minimax_flash_listed_first(models_tokens):
    """Only current models are listed, with Flash first."""
    assert list(models_tokens["minimax"]) == ["MiniMax-M3.1-Flash", "MiniMax-M3"]


def test_minimax_m27_still_available():
    """Saved legacy models retain token metadata outside the current catalog."""
    from scrapegraphai.helpers.models_tokens import MINIMAX_LEGACY_MODEL_TOKENS

    assert MINIMAX_LEGACY_MODEL_TOKENS == {
        "MiniMax-M2.7": 204800,
        "MiniMax-M2.7-highspeed": 204800,
    }


def test_minimax_deprecated_models_removed(models_tokens):
    """Older deprecated MiniMax models should be removed from the list."""
    minimax_models = models_tokens["minimax"]
    assert "MiniMax-M2.5" not in minimax_models
    assert "MiniMax-M2.5-highspeed" not in minimax_models
    assert "MiniMax-M2" not in minimax_models
    assert "MiniMax-M1" not in minimax_models
    assert "MiniMax-M1-40k" not in minimax_models


def test_minimax_token_limits(models_tokens):
    """MiniMax model token limits should match upstream documentation."""
    minimax_models = models_tokens["minimax"]
    assert minimax_models["MiniMax-M3"] == 1000000
    assert minimax_models["MiniMax-M3.1-Flash"] == 1000000


def test_minimax_m27_costs(model_costs):
    """MiniMax-M2.7 should retain all published token rates."""
    assert model_costs.MODEL_COST_PER_1K_TOKENS_INPUT["MiniMax-M2.7"] == 0.0003
    assert model_costs.MODEL_COST_PER_1K_TOKENS_OUTPUT["MiniMax-M2.7"] == 0.0012
    assert model_costs.MODEL_CACHE_COST_PER_1K_TOKENS["MiniMax-M2.7"] == {
        "read": 0.00006,
        "write": 0.000375,
    }


@pytest.mark.parametrize(
    (
        "service_tier",
        "input_tokens",
        "input_rate",
        "output_rate",
        "cache_read_rate",
    ),
    [
        ("standard", 512000, 0.0003, 0.0012, 0.00006),
        ("standard", 512001, 0.0006, 0.0024, 0.00012),
        ("priority", 512000, 0.00045, 0.0018, 0.00009),
        ("priority", 512001, 0.0009, 0.0036, 0.00018),
    ],
)
def test_minimax_m3_tiered_costs(
    model_costs,
    service_tier,
    input_tokens,
    input_rate,
    output_rate,
    cache_read_rate,
):
    """MiniMax-M3 pricing should preserve service and context tiers."""
    assert (
        model_costs.get_model_cost_per_1k_tokens(
            "MiniMax-M3", input_tokens, service_tier=service_tier
        )
        == input_rate
    )
    assert (
        model_costs.get_model_cost_per_1k_tokens(
            "MiniMax-M3",
            input_tokens,
            is_completion=True,
            service_tier=service_tier,
        )
        == output_rate
    )
    tier_index = 0 if input_tokens <= 512000 else 1
    pricing = model_costs.MODEL_COST_TIERS_PER_1K_TOKENS["MiniMax-M3"][service_tier][
        tier_index
    ]
    assert pricing["cache_read"] == cache_read_rate
    assert pricing["cache_write"] is None


def test_minimax_m3_callback_uses_input_token_tier(custom_callback_module):
    """The callback should apply one input tier to both token directions."""
    response = types.SimpleNamespace(
        generations=[[]],
        llm_output={
            "token_usage": {
                "prompt_tokens": 512001,
                "completion_tokens": 1000,
                "total_tokens": 513001,
            }
        },
    )
    callback = custom_callback_module.CustomCallbackHandler("MiniMax-M3")

    callback.on_llm_end(response)

    expected_input_cost = 0.0006 * (512001 / 1000)
    expected_output_cost = 0.0024
    assert callback.total_cost == pytest.approx(
        expected_input_cost + expected_output_cost
    )


def test_minimax_callback_manager_uses_tiered_costs():
    """MiniMax should use its tier-aware callback before the OpenAI fallback."""
    from scrapegraphai.models.minimax import MiniMax
    from scrapegraphai.utils.custom_callback import CustomCallbackHandler
    from scrapegraphai.utils.llm_callback_manager import CustomLLMCallbackManager

    model = MiniMax(
        model="MiniMax-M3",
        api_key="test-key",
        service_tier="priority",
    )

    with CustomLLMCallbackManager().exclusive_get_callback(
        model, "MiniMax-M3"
    ) as callback:
        assert isinstance(callback, CustomCallbackHandler)
        assert callback.service_tier == "priority"


@pytest.mark.parametrize(
    "base_url",
    ["https://api.minimax.io/v1", "https://api.minimaxi.com/v1"],
)
def test_minimax_openai_request_path(minimax_module, base_url):
    """The adapter should preserve either regional OpenAI-compatible base URL."""
    request_urls = []

    def handle_request(request):
        request_urls.append(str(request.url))
        return httpx.Response(
            200,
            request=request,
            json={
                "id": "chatcmpl-test",
                "object": "chat.completion",
                "created": 0,
                "model": "MiniMax-M3",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Done."},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "prompt_tokens": 1,
                    "completion_tokens": 1,
                    "total_tokens": 2,
                },
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handle_request))
    model = minimax_module.MiniMax(
        model="MiniMax-M3",
        api_key="test-key",
        base_url=base_url,
        http_client=http_client,
    )

    model.invoke("Test")

    assert request_urls == [f"{base_url}/chat/completions"]


def test_minimax_defaults_to_global_openai_endpoint(minimax_module):
    """The adapter should keep the global OpenAI-compatible endpoint as default."""
    model = minimax_module.MiniMax(model="MiniMax-M3", api_key="test-key")
    assert str(model.openai_api_base).rstrip("/") == "https://api.minimax.io/v1"


def test_flash_costs(model_costs, custom_callback_module):
    assert model_costs.MODEL_COST_PER_1K_TOKENS_INPUT["MiniMax-M3.1-Flash"] == 0.00015
    assert model_costs.MODEL_COST_PER_1K_TOKENS_OUTPUT["MiniMax-M3.1-Flash"] == 0.0006
    assert model_costs.MODEL_CACHE_COST_PER_1K_TOKENS["MiniMax-M3.1-Flash"] == {
        "read": 0.000015,
        "write": None,
    }
    assert (
        custom_callback_module.get_token_cost_for_model("MiniMax-M3.1-Flash", 1000)
        == 0.00015
    )


@pytest.fixture
def captured_transport():
    requests = []
    tool_call = {
        "id": "call_lookup",
        "type": "function",
        "function": {"name": "lookup", "arguments": '{"query":"page"}'},
    }

    def handle(request):
        body = json.loads(request.content)
        requests.append((str(request.url), body))
        message = {
            "role": "assistant",
            "content": "<think>Keep this.</think>",
            "reasoning_content": "Inspect the page.",
            "tool_calls": [tool_call],
        }
        response = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "created": 0,
            "model": body["model"],
            "choices": [
                {"index": 0, "message": message, "finish_reason": "tool_calls"}
            ],
        }
        if body.get("stream"):
            chunks = []
            for delta in (
                {"role": "assistant", "reasoning_content": "Inspect "},
                {"reasoning_content": "the page."},
                {
                    "content": message["content"],
                    "tool_calls": [{"index": 0, **tool_call}],
                },
            ):
                chunks.append(
                    "data: "
                    + json.dumps(
                        {
                            "id": "chatcmpl-test",
                            "object": "chat.completion.chunk",
                            "created": 0,
                            "model": body["model"],
                            "choices": [
                                {"index": 0, "delta": delta, "finish_reason": None}
                            ],
                        }
                    )
                    + "\n\n"
                )
            return httpx.Response(
                200,
                headers={"content-type": "text/event-stream"},
                text="".join(chunks) + "data: [DONE]\n\n",
            )
        return httpx.Response(200, json=response)

    return requests, httpx.MockTransport(handle)


@pytest.mark.parametrize("base_key", ["base_url", "openai_api_base"])
@pytest.mark.parametrize(
    "base_url", ["https://api.minimax.io/v1", "https://api.minimaxi.com/v1"]
)
@pytest.mark.parametrize(
    "config, expected, tokens",
    [
        ({"model_provider": "minimax"}, "MiniMax-M3.1-Flash", 1000000),
        ({"model": "minimax/MiniMax-M3.1-Flash"}, "MiniMax-M3.1-Flash", 1000000),
        ({"model": "MiniMax-M3"}, "MiniMax-M3", 1000000),
        ({"model": "MiniMax-M2.7"}, "MiniMax-M2.7", 204800),
        ({"model": "minimax/MiniMax-M2.7-highspeed"}, "MiniMax-M2.7-highspeed", 204800),
        (
            {"model": "minimax/custom-model", "model_tokens": 12345},
            "custom-model",
            12345,
        ),
    ],
)
def test_graph_request_models(
    captured_transport, base_key, base_url, config, expected, tokens
):
    from scrapegraphai.graphs.abstract_graph import AbstractGraph

    requests, transport = captured_transport
    graph = types.SimpleNamespace()
    original = dict(config)
    with httpx.Client(transport=transport) as client:
        model = AbstractGraph._create_llm(
            graph,
            {
                **config,
                "api_key": "test-key",
                base_key: base_url,
                "http_client": client,
            },
        )
        model.invoke("Test")
    assert config == original
    assert graph.model_token == tokens
    url, body = requests[0]
    assert url == base_url + "/chat/completions"
    assert body["model"] == expected
    assert "service_tier" not in body
    assert "model_tokens" not in body


@pytest.mark.parametrize("streaming", [False, True])
@pytest.mark.parametrize("effort", ["low", "medium", "high", "xhigh", "max"])
def test_flash_tool_history_and_images(
    minimax_module, captured_transport, streaming, effort
):
    from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

    requests, transport = captured_transport
    image = {
        "type": "image_url",
        "image_url": {"url": "data:image/png;base64,dGVzdA=="},
    }
    video = {"type": "video_url", "video_url": {"url": "https://example.com/video.mp4"}}
    history = [
        SystemMessage("Extract the page."),
        HumanMessage(
            [
                {"type": "text", "text": "Read this."},
                image,
                video,
            ]
        ),
    ]
    tool = {
        "type": "function",
        "function": {
            "name": "lookup",
            "description": "Look up a page.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
            },
        },
    }
    with httpx.Client(transport=transport) as client:
        model = minimax_module.MiniMax(
            api_key="test-key",
            http_client=client,
            streaming=streaming,
            reasoning_effort=effort,
            max_tokens=524288,
            extra_body={"thinking": {"type": "adaptive"}},
        ).bind_tools([tool])
        answer = model.invoke(history)
        assert answer.additional_kwargs["reasoning_content"] == "Inspect the page."
        model.invoke(
            history + [answer, ToolMessage("Result", tool_call_id="call_lookup")]
        )
    body = requests[1][1]
    assert body["model"] == "MiniMax-M3.1-Flash"
    assert body["reasoning_effort"] == effort
    assert body["max_completion_tokens"] == 524288
    assert body["thinking"] == {"type": "adaptive"}
    assert "service_tier" not in body
    assert body["tools"] == [tool]
    assert body["messages"][0] == {"role": "system", "content": "Extract the page."}
    assert body["messages"][1]["content"][1:] == [image, video]
    assert body["messages"][2]["reasoning_content"] == "Inspect the page."
    assert body["messages"][2]["content"] == "<think>Keep this.</think>"
    assert body["messages"][2]["tool_calls"][0]["id"] == "call_lookup"
    assert body["messages"][3] == {
        "role": "tool",
        "content": "Result",
        "tool_call_id": "call_lookup",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("streaming", [False, True])
async def test_async_m3_history_preserves_disabled_thinking(
    minimax_module, captured_transport, streaming
):
    from langchain_core.messages import ToolMessage

    requests, transport = captured_transport
    async with httpx.AsyncClient(transport=transport) as client:
        model = minimax_module.MiniMax(
            model="MiniMax-M3",
            api_key="test-key",
            http_async_client=client,
            streaming=streaming,
            extra_body={"thinking": {"type": "disabled"}},
        )
        answer = await model.ainvoke("Test")
        await model.ainvoke(
            [
                ("user", "Test"),
                answer,
                ToolMessage("Result", tool_call_id="call_lookup"),
            ]
        )
    assert requests[1][1]["model"] == "MiniMax-M3"
    assert requests[1][1]["thinking"] == {"type": "disabled"}
    assert requests[1][1]["messages"][1]["reasoning_content"] == "Inspect the page."


def test_flash_usage_callback(captured_transport):
    from scrapegraphai.models.minimax import MiniMax
    from scrapegraphai.utils.llm_callback_manager import CustomLLMCallbackManager

    _, transport = captured_transport
    with httpx.Client(transport=transport) as client:
        model = MiniMax(api_key="test-key", http_client=client)
        with CustomLLMCallbackManager().exclusive_get_callback(
            model, model.model_name
        ) as callback:
            callback.on_llm_end(
                types.SimpleNamespace(
                    generations=[[]],
                    llm_output={
                        "token_usage": {
                            "prompt_tokens": 1000,
                            "completion_tokens": 1000,
                            "total_tokens": 2000,
                        },
                    },
                )
            )
    assert callback.total_cost == pytest.approx(0.00075)


def test_explicit_model_alias_and_custom_endpoint(minimax_module, captured_transport):
    requests, transport = captured_transport
    with httpx.Client(transport=transport) as client:
        model = minimax_module.MiniMax(
            model_name="saved-model",
            api_key="test-key",
            base_url="https://custom.example/v1",
            http_client=client,
        )
        model.invoke("Test")
    assert requests[0][0] == "https://custom.example/v1/chat/completions"
    assert requests[0][1]["model"] == "saved-model"
