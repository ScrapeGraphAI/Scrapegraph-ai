from unittest.mock import Mock, patch

import pytest
from pydantic import BaseModel, Field

from scrapegraphai.graphs.json_scraper_graph import JSONScraperGraph


class TestJSONScraperGraph:
    @pytest.fixture
    def mock_llm_model(self):
        return Mock()

    @pytest.fixture
    def mock_embedder_model(self):
        return Mock()

    @patch("scrapegraphai.graphs.json_scraper_graph.FetchNode")
    @patch("scrapegraphai.graphs.json_scraper_graph.GenerateAnswerNode")
    @patch.object(JSONScraperGraph, "_create_llm")
    def test_json_scraper_graph_with_directory(
        self,
        mock_create_llm,
        mock_generate_answer_node,
        mock_fetch_node,
        mock_llm_model,
        mock_embedder_model,
    ):
        """
        Test JSONScraperGraph with a directory of JSON files.
        This test checks if the graph correctly handles multiple JSON files input
        and processes them to generate an answer.
        """
        # Mock the _create_llm method to return a mock LLM model
        mock_create_llm.return_value = mock_llm_model

        # Mock the execute method of BaseGraph
        with patch(
            "scrapegraphai.graphs.json_scraper_graph.BaseGraph.execute"
        ) as mock_execute:
            mock_execute.return_value = (
                {"answer": "Mocked answer for multiple JSON files"},
                {},
            )

            # Create a JSONScraperGraph instance
            graph = JSONScraperGraph(
                prompt="Summarize the data from all JSON files",
                source="path/to/json/directory",
                config={"llm": {"model": "test-model", "temperature": 0}},
                schema=BaseModel,
            )

            # Set mocked embedder model
            graph.embedder_model = mock_embedder_model

            # Run the graph
            result = graph.run()

            # Assertions
            assert result == "Mocked answer for multiple JSON files"
            assert graph.input_key == "json_dir"
            mock_execute.assert_called_once_with(
                {
                    "user_prompt": "Summarize the data from all JSON files",
                    "json_dir": "path/to/json/directory",
                }
            )
            mock_fetch_node.assert_called_once()
            mock_generate_answer_node.assert_called_once()
            mock_create_llm.assert_called_once_with(
                {"model": "test-model", "temperature": 0}
            )

    @patch("scrapegraphai.graphs.json_scraper_graph.FetchNode")
    @patch("scrapegraphai.graphs.json_scraper_graph.GenerateAnswerNode")
    @patch.object(JSONScraperGraph, "_create_llm")
    def test_json_scraper_graph_with_single_file(
        self,
        mock_create_llm,
        mock_generate_answer_node,
        mock_fetch_node,
        mock_llm_model,
        mock_embedder_model,
    ):
        """
        Test JSONScraperGraph with a single JSON file.
        This test checks if the graph correctly handles a single JSON file input
        and processes it to generate an answer.
        """
        # Mock the _create_llm method to return a mock LLM model
        mock_create_llm.return_value = mock_llm_model

        # Mock the execute method of BaseGraph
        with patch(
            "scrapegraphai.graphs.json_scraper_graph.BaseGraph.execute"
        ) as mock_execute:
            mock_execute.return_value = (
                {"answer": "Mocked answer for single JSON file"},
                {},
            )

            # Create a JSONScraperGraph instance with a single JSON file
            graph = JSONScraperGraph(
                prompt="Analyze the data from the JSON file",
                source="path/to/single/file.json",
                config={"llm": {"model": "test-model", "temperature": 0}},
                schema=BaseModel,
            )

            # Set mocked embedder model
            graph.embedder_model = mock_embedder_model

            # Run the graph
            result = graph.run()

            # Assertions
            assert result == "Mocked answer for single JSON file"
            assert graph.input_key == "json"
            mock_execute.assert_called_once_with(
                {
                    "user_prompt": "Analyze the data from the JSON file",
                    "json": "path/to/single/file.json",
                }
            )
            mock_fetch_node.assert_called_once()
            mock_generate_answer_node.assert_called_once()
            mock_create_llm.assert_called_once_with(
                {"model": "test-model", "temperature": 0}
            )

    @patch("scrapegraphai.graphs.json_scraper_graph.FetchNode")
    @patch("scrapegraphai.graphs.json_scraper_graph.GenerateAnswerNode")
    @patch.object(JSONScraperGraph, "_create_llm")
    def test_json_scraper_graph_no_answer_found(
        self,
        mock_create_llm,
        mock_generate_answer_node,
        mock_fetch_node,
        mock_llm_model,
        mock_embedder_model,
    ):
        """
        Test JSONScraperGraph when no answer is found.
        This test checks if the graph correctly handles the scenario where no answer is generated,
        ensuring it returns the default "No answer found." message.
        """
        # Mock the _create_llm method to return a mock LLM model
        mock_create_llm.return_value = mock_llm_model

        # Mock the execute method of BaseGraph to return an empty answer
        with patch(
            "scrapegraphai.graphs.json_scraper_graph.BaseGraph.execute"
        ) as mock_execute:
            mock_execute.return_value = ({}, {})  # Empty state and execution info

            # Create a JSONScraperGraph instance
            graph = JSONScraperGraph(
                prompt="Query that produces no answer",
                source="path/to/empty/file.json",
                config={"llm": {"model": "test-model", "temperature": 0}},
                schema=BaseModel,
            )

            # Set mocked embedder model
            graph.embedder_model = mock_embedder_model

            # Run the graph
            result = graph.run()

            # Assertions
            assert result == "No answer found."
            assert graph.input_key == "json"
            mock_execute.assert_called_once_with(
                {
                    "user_prompt": "Query that produces no answer",
                    "json": "path/to/empty/file.json",
                }
            )
            mock_fetch_node.assert_called_once()
            mock_generate_answer_node.assert_called_once()
            mock_create_llm.assert_called_once_with(
                {"model": "test-model", "temperature": 0}
            )

    @patch("scrapegraphai.graphs.json_scraper_graph.FetchNode")
    @patch("scrapegraphai.graphs.json_scraper_graph.GenerateAnswerNode")
    @patch.object(JSONScraperGraph, "_create_llm")
    def test_json_scraper_graph_with_custom_schema(
        self,
        mock_create_llm,
        mock_generate_answer_node,
        mock_fetch_node,
        mock_llm_model,
        mock_embedder_model,
    ):
        """
        Test JSONScraperGraph with a custom schema.
        This test checks if the graph correctly handles a custom schema input
        and passes it to the GenerateAnswerNode.
        """

        # Define a custom schema
        class CustomSchema(BaseModel):
            name: str = Field(..., description="Name of the attraction")
            description: str = Field(..., description="Description of the attraction")

        # Mock the _create_llm method to return a mock LLM model
        mock_create_llm.return_value = mock_llm_model

        # Mock the execute method of BaseGraph
        with patch(
            "scrapegraphai.graphs.json_scraper_graph.BaseGraph.execute"
        ) as mock_execute:
            mock_execute.return_value = (
                {"answer": "Mocked answer with custom schema"},
                {},
            )

            # Create a JSONScraperGraph instance with a custom schema
            graph = JSONScraperGraph(
                prompt="List attractions in Chioggia",
                source="path/to/chioggia.json",
                config={"llm": {"model": "test-model", "temperature": 0}},
                schema=CustomSchema,
            )

            # Set mocked embedder model
            graph.embedder_model = mock_embedder_model

            # Run the graph
            result = graph.run()

            # Assertions
            assert result == "Mocked answer with custom schema"
            assert graph.input_key == "json"
            mock_execute.assert_called_once_with(
                {
                    "user_prompt": "List attractions in Chioggia",
                    "json": "path/to/chioggia.json",
                }
            )
            mock_fetch_node.assert_called_once()
            mock_generate_answer_node.assert_called_once()

            # Check if the custom schema was passed to GenerateAnswerNode
            generate_answer_node_call = mock_generate_answer_node.call_args[1]
            assert generate_answer_node_call["node_config"]["schema"] == CustomSchema

            mock_create_llm.assert_called_once_with(
                {"model": "test-model", "temperature": 0}
            )
