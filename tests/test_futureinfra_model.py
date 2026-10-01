"""Tests for FutureInfra model configuration."""

import importlib.util
import os


def test_futureinfra_model_sets_openai_compatible_base_url():
    """FutureInfra should map api_key and set its base URL."""
    spec = importlib.util.spec_from_file_location(
        "futureinfra",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "scrapegraphai",
            "models",
            "futureinfra.py",
        ),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    model = module.FutureInfra(
        api_key="test-key",
        model="openai/gpt-4o-mini",
    )

    assert str(model.openai_api_base).rstrip("/") == "https://futureinfra.ai/v1/ai"
    assert model.openai_api_key.get_secret_value() == "test-key"


def test_futureinfra_models_in_token_list():
    """FutureInfra defaults should be listed with their context lengths."""
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

    futureinfra_models = module.models_tokens["futureinfra"]
    assert futureinfra_models["openai/gpt-4o-mini"] == 128000
    assert futureinfra_models["openai/gpt-4o"] == 128000
