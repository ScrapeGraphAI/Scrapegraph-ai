"""Tests for MiniMax model configuration."""

import importlib.util
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


def test_minimax_m3_listed_first(models_tokens):
    """MiniMax-M3 should be the first (default) model in the minimax dict."""
    minimax_models = list(models_tokens["minimax"].keys())
    assert minimax_models[0] == "MiniMax-M3"


def test_minimax_m27_still_available(models_tokens):
    """MiniMax-M2.7 and its highspeed variant should remain as legacy options."""
    minimax_models = models_tokens["minimax"]
    assert "MiniMax-M2.7" in minimax_models
    assert "MiniMax-M2.7-highspeed" in minimax_models


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
    assert minimax_models["MiniMax-M2.7"] == 204800
    assert minimax_models["MiniMax-M2.7-highspeed"] == 204800


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
