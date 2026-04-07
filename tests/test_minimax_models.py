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


def test_minimax_m27_in_model_list(models_tokens):
    """MiniMax-M2.7 and MiniMax-M2.7-highspeed should be in the model list."""
    minimax_models = models_tokens["minimax"]
    assert "MiniMax-M2.7" in minimax_models
    assert "MiniMax-M2.7-highspeed" in minimax_models


def test_minimax_m27_listed_first(models_tokens):
    """MiniMax-M2.7 should be the first model in the minimax dict."""
    minimax_models = list(models_tokens["minimax"].keys())
    assert minimax_models[0] == "MiniMax-M2.7"
    assert minimax_models[1] == "MiniMax-M2.7-highspeed"


def test_minimax_old_models_still_present(models_tokens):
    """All previous MiniMax models should still be available."""
    minimax_models = models_tokens["minimax"]
    assert "MiniMax-M2.5" in minimax_models
    assert "MiniMax-M2.5-highspeed" in minimax_models
    assert "MiniMax-M2" in minimax_models
    assert "MiniMax-M1" in minimax_models


def test_minimax_m27_token_limits(models_tokens):
    """MiniMax-M2.7 models should have correct token limits."""
    minimax_models = models_tokens["minimax"]
    assert minimax_models["MiniMax-M2.7"] == 204000
    assert minimax_models["MiniMax-M2.7-highspeed"] == 204000
