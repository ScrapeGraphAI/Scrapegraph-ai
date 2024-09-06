"""
Tests for the AbstractGraph.
"""
import pytest
from unittest.mock import patch
from scrapegraphai.graphs import AbstractGraph, BaseGraph
from scrapegraphai.nodes import (
    FetchNode,
    ParseNode
)
from scrapegraphai.models import OneApi, DeepSeek
from langchain_openai import ChatOpenAI, AzureChatOpenAI
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_aws import ChatBedrock



class TestGraph(AbstractGraph):
    def __init__(self, prompt: str, config: dict):
        super().__init__(prompt, config)

    def _create_graph(self) -> BaseGraph:
        fetch_node = FetchNode(
            input="url| local_dir",
            output=["doc"],
            node_config={
                "llm_model": self.llm_model,
                "force": self.config.get("force", False),
                "cut": self.config.get("cut", True),
                "loader_kwargs": self.config.get("loader_kwargs", {}),
                "browser_base": self.config.get("browser_base")
            }
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "llm_model": self.llm_model,
                "chunk_size": self.model_token
            }
        )
        return BaseGraph(
            nodes=[
                fetch_node,
                parse_node
            ],
            edges=[
                (fetch_node, parse_node),
            ],
            entry_point=fetch_node,
            graph_name=self.__class__.__name__
        )

    def run(self) -> str:
        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")


class TestAbstractGraph:
    @pytest.mark.parametrize("llm_config, expected_model", [
        ({"model": "openai/gpt-3.5-turbo", "openai_api_key": "sk-randomtest001"}, ChatOpenAI),
        ({
            "model": "azure_openai/gpt-3.5-turbo",
            "api_key": "random-api-key",
            "api_version": "no version",
            "azure_endpoint": "https://www.example.com/"},
            AzureChatOpenAI),
        ({"model": "google_genai/gemini-pro", "google_api_key": "google-key-test"}, ChatGoogleGenerativeAI),
        ({"model": "ollama/llama2"}, ChatOllama),
        ({"model": "oneapi/qwen-turbo", "api_key": "oneapi-api-key"}, OneApi),
        ({"model": "deepseek/deepseek-coder", "api_key": "deepseek-api-key"}, DeepSeek),
        ({"model": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0", "region_name": "IDK"}, ChatBedrock),
    ])

    def test_create_llm(self, llm_config, expected_model):
        graph = TestGraph("Test prompt", {"llm": llm_config})
        assert isinstance(graph.llm_model, expected_model)

    def test_create_llm_unknown_provider(self):
        with pytest.raises(ValueError):
            TestGraph("Test prompt", {"llm": {"model": "unknown_provider/model"}})

    @pytest.mark.parametrize("llm_config, expected_model", [
        ({"model": "openai/gpt-3.5-turbo", "openai_api_key": "sk-randomtest001", "rate_limit": {"requests_per_second": 1}}, ChatOpenAI),
        ({"model": "azure_openai/gpt-3.5-turbo", "api_key": "random-api-key", "api_version": "no version", "azure_endpoint": "https://www.example.com/", "rate_limit": {"requests_per_second": 1}}, AzureChatOpenAI),
        ({"model": "google_genai/gemini-pro", "google_api_key": "google-key-test", "rate_limit": {"requests_per_second": 1}}, ChatGoogleGenerativeAI),
        ({"model": "ollama/llama2", "rate_limit": {"requests_per_second": 1}}, ChatOllama),
        ({"model": "oneapi/qwen-turbo", "api_key": "oneapi-api-key", "rate_limit": {"requests_per_second": 1}}, OneApi),
        ({"model": "deepseek/deepseek-coder", "api_key": "deepseek-api-key", "rate_limit": {"requests_per_second": 1}}, DeepSeek),
        ({"model": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0", "region_name": "IDK", "rate_limit": {"requests_per_second": 1}}, ChatBedrock),
    ])


    def test_create_llm_with_rate_limit(self, llm_config, expected_model):
        graph = TestGraph("Test prompt", {"llm": llm_config})
        assert isinstance(graph.llm_model, expected_model)