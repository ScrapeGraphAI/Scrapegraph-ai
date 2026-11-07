"""Tests for the CloudGPU model configuration."""

import importlib.util
import os
from unittest.mock import Mock, patch

from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.models.cloudgpu import CloudGPU


def _load_models_tokens():
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


def test_cloudgpu_model_sets_openai_compatible_base_url():
    """CloudGPU should map api_key and default to the CloudGPU base URL."""
    model = CloudGPU(api_key="test-key", model="deepseek-v4-flash")

    assert str(model.openai_api_base).rstrip("/") == "https://cloudgpu.app/v1"
    assert model.openai_api_key.get_secret_value() == "test-key"


def test_cloudgpu_model_keeps_custom_base_url():
    """An explicit base_url is not overwritten."""
    model = CloudGPU(
        api_key="test-key",
        model="deepseek-v4-flash",
        base_url="https://example.com/v1",
    )

    assert str(model.openai_api_base).rstrip("/") == "https://example.com/v1"


def test_cloudgpu_models_in_token_list():
    """CloudGPU defaults should be listed with their context lengths."""
    cloudgpu_models = _load_models_tokens()["cloudgpu"]

    assert cloudgpu_models["deepseek-v4-flash"] == 131072
    assert cloudgpu_models["kimi-k2.6"] == 262144


def test_cloudgpu_provider_resolves_from_model_prefix():
    """`cloudgpu/<model>` resolves to CloudGPU with the bare model id."""
    config = {
        "llm": {
            "model": "cloudgpu/deepseek-v4-flash",
            "api_key": "test-key",
        }
    }
    with patch.object(SmartScraperGraph, "_create_graph", return_value=Mock(nodes=[])):
        graph = SmartScraperGraph("prompt", "https://example.com", config)

    assert isinstance(graph.llm_model, CloudGPU)
    assert graph.llm_model.model_name == "deepseek-v4-flash"
    assert graph.model_token == 131072
    assert not getattr(graph, "model_tokens_defaulted", False)
