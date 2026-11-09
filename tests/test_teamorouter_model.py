"""Tests for TeamoRouter model configuration."""

import importlib.util
import os


def _load(name, *parts):
    spec = importlib.util.spec_from_file_location(
        name, os.path.join(os.path.dirname(__file__), "..", "scrapegraphai", *parts)
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_teamorouter_model_sets_openai_compatible_base_url():
    """TeamoRouter should map api_key, set its base URL and tag requests."""
    module = _load("teamorouter", "models", "teamorouter.py")

    model = module.TeamoRouter(api_key="test-key", model="deepseek-v4-flash")

    assert str(model.openai_api_base).rstrip("/") == "https://api.teamorouter.com/v1"
    assert model.openai_api_key.get_secret_value() == "test-key"
    assert model.default_headers["X-Client-Source"] == "scrapegraphai-teamorouter"


def test_teamorouter_model_keeps_user_headers():
    """Headers passed by the caller are kept and can override the default tag."""
    module = _load("teamorouter", "models", "teamorouter.py")

    model = module.TeamoRouter(
        api_key="test-key",
        model="deepseek-v4-flash",
        default_headers={"X-Client-Source": "my-app", "X-Trace": "1"},
    )

    assert model.default_headers["X-Client-Source"] == "my-app"
    assert model.default_headers["X-Trace"] == "1"


def test_teamorouter_models_in_token_list():
    """TeamoRouter defaults should be listed with their context lengths."""
    module = _load("models_tokens", "helpers", "models_tokens.py")

    teamorouter_models = module.models_tokens["teamorouter"]
    assert teamorouter_models["deepseek-v4-flash"] == 1000000
    assert teamorouter_models["qwen3.8-flash"] == 1000000
