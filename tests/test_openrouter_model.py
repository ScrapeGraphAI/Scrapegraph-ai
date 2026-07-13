"""Tests for the OpenRouter model configuration."""
import importlib.util
import os


def test_openrouter_model_sets_openai_compatible_base_url():
    """OpenRouter should map api_key and set the OpenRouter base URL."""
    spec = importlib.util.spec_from_file_location(
        "openrouter",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "scrapegraphai",
            "models",
            "openrouter.py",
        ),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    model = module.OpenRouter(
        api_key="test-key",
        model="openrouter/anthropic/claude-3.5-sonnet",
    )

    assert str(model.openai_api_base).rstrip("/") == "https://openrouter.ai/api/v1"
    assert model.openai_api_key == "test-key"
