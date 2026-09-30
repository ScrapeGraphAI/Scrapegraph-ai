"""Tests for the API Route model wrapper."""

import importlib.util
from pathlib import Path


def test_apiroute_uses_fixed_endpoint_and_api_key():
    """The wrapper should configure ChatOpenAI without making a network call."""
    model_path = (
        Path(__file__).resolve().parents[1] / "scrapegraphai/models/apiroute.py"
    )
    spec = importlib.util.spec_from_file_location("apiroute", model_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    model = module.APIRoute(api_key="test-key", model="gpt-5.5")

    assert str(model.openai_api_base).rstrip("/") == "https://global.api-route.com/v1"
    assert model.openai_api_key.get_secret_value() == "test-key"
