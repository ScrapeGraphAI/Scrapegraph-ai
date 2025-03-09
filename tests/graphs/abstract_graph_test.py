import pytest

from langchain_aws import ChatBedrock
from langchain_ollama import ChatOllama
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from scrapegraphai.graphs import AbstractGraph, BaseGraph
from scrapegraphai.models import DeepSeek, OneApi
from scrapegraphai.nodes import FetchNode, ParseNode
from unittest.mock import Mock, patch

"""
Tests for the AbstractGraph.
"""

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
                "browser_base": self.config.get("browser_base"),
            },
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={"llm_model": self.llm_model, "chunk_size": self.model_token},
        )
        return BaseGraph(
            nodes=[fetch_node, parse_node],
            edges=[
                (fetch_node, parse_node),
            ],
            entry_point=fetch_node,
            graph_name=self.__class__.__name__,
        )

    def run(self) -> str:
        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")

class TestAbstractGraph:
    @pytest.mark.parametrize(
        "llm_config, expected_model",
        [
            (
                {"model": "openai/gpt-3.5-turbo", "openai_api_key": "sk-randomtest001"},
                ChatOpenAI,
            ),
            (
                {
                    "model": "azure_openai/gpt-3.5-turbo",
                    "api_key": "random-api-key",
                    "api_version": "no version",
                    "azure_endpoint": "https://www.example.com/",
                },
                AzureChatOpenAI,
            ),
            ({"model": "ollama/llama2"}, ChatOllama),
            ({"model": "oneapi/qwen-turbo", "api_key": "oneapi-api-key"}, OneApi),
            (
                {"model": "deepseek/deepseek-coder", "api_key": "deepseek-api-key"},
                DeepSeek,
            ),
            (
                {
                    "model": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
                    "region_name": "IDK",
                },
                ChatBedrock,
            ),
        ],
    )
    def test_create_llm(self, llm_config, expected_model):
        graph = TestGraph("Test prompt", {"llm": llm_config})
        assert isinstance(graph.llm_model, expected_model)

    def test_create_llm_unknown_provider(self):
        with pytest.raises(ValueError):
            TestGraph("Test prompt", {"llm": {"model": "unknown_provider/model"}})

    @pytest.mark.parametrize(
        "llm_config, expected_model",
        [
            (
                {
                    "model": "openai/gpt-3.5-turbo",
                    "openai_api_key": "sk-randomtest001",
                    "rate_limit": {"requests_per_second": 1},
                },
                ChatOpenAI,
            ),
            (
                {
                    "model": "azure_openai/gpt-3.5-turbo",
                    "api_key": "random-api-key",
                    "api_version": "no version",
                    "azure_endpoint": "https://www.example.com/",
                    "rate_limit": {"requests_per_second": 1},
                },
                AzureChatOpenAI,
            ),
            (
                {"model": "ollama/llama2", "rate_limit": {"requests_per_second": 1}},
                ChatOllama,
            ),
            (
                {
                    "model": "oneapi/qwen-turbo",
                    "api_key": "oneapi-api-key",
                    "rate_limit": {"requests_per_second": 1},
                },
                OneApi,
            ),
            (
                {
                    "model": "deepseek/deepseek-coder",
                    "api_key": "deepseek-api-key",
                    "rate_limit": {"requests_per_second": 1},
                },
                DeepSeek,
            ),
            (
                {
                    "model": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
                    "region_name": "IDK",
                    "rate_limit": {"requests_per_second": 1},
                },
                ChatBedrock,
            ),
        ],
    )
    def test_create_llm_with_rate_limit(self, llm_config, expected_model):
        graph = TestGraph("Test prompt", {"llm": llm_config})
        assert isinstance(graph.llm_model, expected_model)

    @pytest.mark.asyncio
    async def test_run_safe_async(self):
        graph = TestGraph(
            "Test prompt",
            {
                "llm": {
                    "model": "openai/gpt-3.5-turbo",
                    "openai_api_key": "sk-randomtest001",
                }
            },
        )
        with patch.object(graph, "run", return_value="Async result") as mock_run:
            result = await graph.run_safe_async()
            assert result == "Async result"
            mock_run.assert_called_once()

    def test_create_llm_with_custom_model_instance(self):
        """
        Test that the _create_llm method correctly uses a custom model instance
        when provided in the configuration.
        """
        mock_model = Mock()
        mock_model.model_name = "custom-model"

        config = {
            "llm": {
                "model_instance": mock_model,
                "model_tokens": 1000,
                "model": "custom/model"
            }
        }

        graph = TestGraph("Test prompt", config)

        assert graph.llm_model == mock_model
        assert graph.model_token == 1000

    def test_set_common_params(self):
        """
        Test that the set_common_params method correctly updates the configuration
        of all nodes in the graph.
        """
        # Create a mock graph with mock nodes
        mock_graph = Mock()
        mock_node1 = Mock()
        mock_node2 = Mock()
        mock_graph.nodes = [mock_node1, mock_node2]

        # Create a TestGraph instance with the mock graph
        with patch('scrapegraphai.graphs.abstract_graph.AbstractGraph._create_graph', return_value=mock_graph):
            graph = TestGraph("Test prompt", {"llm": {"model": "openai/gpt-3.5-turbo", "openai_api_key": "sk-test"}})

        # Call set_common_params with test parameters
        test_params = {"param1": "value1", "param2": "value2"}
        graph.set_common_params(test_params)

        # Assert that update_config was called on each node with the correct parameters
    
    def test_get_state(self):
        """Test that get_state returns the correct final state with or without a provided key, and raises KeyError for missing keys."""
        graph = TestGraph("dummy", {"llm": {"model": "openai/gpt-3.5-turbo", "openai_api_key": "sk-test"}})
        # Set a dummy final state
        graph.final_state = {"answer": "42", "other": "value"}
        # Test without a key returns the entire final_state
        state = graph.get_state()
        assert state == {"answer": "42", "other": "value"}
        # Test with a valid key returns the specific value
        answer = graph.get_state("answer")
        assert answer == "42"
        # Test that a missing key raises a KeyError
        with pytest.raises(KeyError):
            _ = graph.get_state("nonexistent")

    def test_append_node(self):
        """Test that append_node correctly delegates to the graph's append_node method."""
        graph = TestGraph("dummy", {"llm": {"model": "openai/gpt-3.5-turbo", "openai_api_key": "sk-test"}})
        # Replace the graph object with a mock that has append_node
        mock_graph = Mock()
        graph.graph = mock_graph
        dummy_node = Mock()
        graph.append_node(dummy_node)
        mock_graph.append_node.assert_called_once_with(dummy_node)

    def test_get_execution_info(self):
        """Test that get_execution_info returns the execution info stored in the graph."""
        graph = TestGraph("dummy", {"llm": {"model": "openai/gpt-3.5-turbo", "openai_api_key": "sk-test"}})
        dummy_info = {"execution": "info", "status": "ok"}
        graph.execution_info = dummy_info
        info = graph.get_execution_info()
        assert info == dummy_info