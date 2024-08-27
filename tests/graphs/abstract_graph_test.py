"""
Tests for the AbstractGraph.
"""
import pytest
from unittest.mock import patch
from scrapegraphai.graphs import AbstractGraph

class TestAbstractGraph:
    @pytest.mark.parametrize("llm_config, expected_model", [
        ({"model": "openai/gpt-3.5-turbo"}, "ChatOpenAI"),
        ({"model": "azure_openai/gpt-3.5-turbo"}, "AzureChatOpenAI"),
        ({"model": "google_genai/gemini-pro"}, "ChatGoogleGenerativeAI"),
        ({"model": "google_vertexai/chat-bison"}, "ChatVertexAI"),
        ({"model": "ollama/llama2"}, "Ollama"),
        ({"model": "oneapi/text-davinci-003"}, "OneApi"),
        ({"model": "nvidia/clara-instant-1-base"}, "ChatNVIDIA"),
        ({"model": "deepseek/deepseek-coder-6.7b-instruct"}, "DeepSeek"),
        ({"model": "ernie/ernie-bot"}, "ErnieBotChat"),
    ])
    def test_create_llm(self, llm_config, expected_model):
        graph = AbstractGraph("Test prompt", {"llm": llm_config})
        assert isinstance(graph.llm_model, expected_model)

    def test_create_llm_unknown_provider(self):
        with pytest.raises(ValueError):
            AbstractGraph("Test prompt", {"llm": {"model": "unknown_provider/model"}})

    def test_create_llm_error(self):
        with patch("your_module.init_chat_model", side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                AbstractGraph("Test prompt", {"llm": {"model": "openai/gpt-3.5-turbo"}})
