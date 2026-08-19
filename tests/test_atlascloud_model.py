"""Tests for Atlas Cloud model configuration."""

import importlib.util
import os


def test_atlascloud_model_sets_openai_compatible_base_url():
    """AtlasCloud should map api_key and set the Atlas Cloud base URL."""
    spec = importlib.util.spec_from_file_location(
        "atlascloud",
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "scrapegraphai",
            "models",
            "atlascloud.py",
        ),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    model = module.AtlasCloud(
        api_key="test-key",
        model="qwen/qwen3.5-flash",
    )

    assert str(model.openai_api_base).rstrip("/") == "https://api.atlascloud.ai/v1"
    assert model.openai_api_key.get_secret_value() == "test-key"


def test_atlascloud_models_in_token_list():
    """Atlas Cloud defaults should be listed with current context lengths."""
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

    atlascloud_models = module.models_tokens["atlascloud"]
    assert atlascloud_models["deepseek-ai/deepseek-v4-pro"] == 1048576
    assert atlascloud_models["qwen/qwen3.5-flash"] == 1000000
