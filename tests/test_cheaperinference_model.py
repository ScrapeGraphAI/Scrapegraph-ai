"""Tests for Cheaper Inference model configuration."""

import importlib.util
import os


def test_cheaperinference_model_sets_openai_compatible_base_url():
    """CheaperInference should map api_key and set its base URL."""
    spec = importlib.util.spec_from_file_location(
        "cheaperinference",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "scrapegraphai",
            "models",
            "cheaperinference.py",
        ),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    model = module.CheaperInference(
        api_key="test-key",
        model="gpt-5.4-mini",
    )

    assert (
        str(model.openai_api_base).rstrip("/") == "https://api.cheaperinference.com/v1"
    )
    assert model.openai_api_key.get_secret_value() == "test-key"


def test_cheaperinference_models_in_token_list():
    """Cheaper Inference defaults should be listed with current context lengths."""
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

    cheaperinference_models = module.models_tokens["cheaperinference"]
    assert cheaperinference_models["gpt-5.4-mini"] == 400000
    assert cheaperinference_models["gpt-5.4"] == 1000000
