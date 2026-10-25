"""Tests for the Runcrate model configuration."""

from unittest.mock import Mock, patch

from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.models import Runcrate


def test_runcrate_model_sets_openai_compatible_base_url():
    """Runcrate should map api_key and pin its base URL."""
    model = Runcrate(api_key="test-key", model="deepseek-ai/DeepSeek-V4.1-Flash")

    assert str(model.openai_api_base).rstrip("/") == "https://api.runcrate.ai/v1"
    assert model.openai_api_key.get_secret_value() == "test-key"


def test_runcrate_provider_keeps_vendor_prefixed_model_id():
    """`runcrate/<vendor>/<model>` resolves to Runcrate with the full model id."""
    config = {
        "llm": {
            "model": "runcrate/deepseek-ai/DeepSeek-V4.1-Flash",
            "api_key": "test-key",
        }
    }
    with patch.object(SmartScraperGraph, "_create_graph", return_value=Mock(nodes=[])):
        graph = SmartScraperGraph("prompt", "https://example.com", config)

    assert isinstance(graph.llm_model, Runcrate)
    assert graph.llm_model.model_name == "deepseek-ai/DeepSeek-V4.1-Flash"
    assert graph.model_token == 1048576
    assert not getattr(graph, "model_tokens_defaulted", False)
