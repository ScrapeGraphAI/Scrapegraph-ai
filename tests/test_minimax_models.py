"""Tests for MiniMax model configuration."""

import importlib.util
import os
import sys

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
    assert minimax_models["MiniMax-M3"] == 524288
    assert minimax_models["MiniMax-M2.7"] == 204000
    assert minimax_models["MiniMax-M2.7-highspeed"] == 204000
