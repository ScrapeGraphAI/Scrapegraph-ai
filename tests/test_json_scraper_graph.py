import pytest

from pydantic import BaseModel
from scrapegraphai.graphs.json_scraper_graph import JSONScraperGraph
from unittest.mock import Mock, patch

class TestJSONScraperGraph:
    @pytest.fixture
    def mock_llm_model(self):
        return Mock()

    @pytest.fixture
    def mock_embedder_model(self):
        return Mock()

    @patch('scrapegraphai.graphs.json_scraper_graph.FetchNode')
    @patch('scrapegraphai.graphs.json_scraper_graph.GenerateAnswerNode')
    @patch.object(JSONScraperGraph, '_create_llm')
    def test_json_scraper_graph_with_directory(self, mock_create_llm, mock_generate_answer_node, mock_fetch_node, mock_llm_model, mock_embedder_model):
        """
        Test JSONScraperGraph with a directory of JSON files.
        This test checks if the graph correctly handles multiple JSON files input
        and processes them to generate an answer.
        """
        # Mock the _create_llm method to return a mock LLM model
        mock_create_llm.return_value = mock_llm_model

        # Mock the execute method of BaseGraph
        with patch('scrapegraphai.graphs.json_scraper_graph.BaseGraph.execute') as mock_execute:
            mock_execute.return_value = ({"answer": "Mocked answer for multiple JSON files"}, {})

            # Create a JSONScraperGraph instance
            graph = JSONScraperGraph(
                prompt="Summarize the data from all JSON files",
                source="path/to/json/directory",
                config={"llm": {"model": "test-model", "temperature": 0}},
                schema=BaseModel
            )

            # Set mocked embedder model
            graph.embedder_model = mock_embedder_model

            # Run the graph
            result = graph.run()

            # Assertions
            assert result == "Mocked answer for multiple JSON files"
            assert graph.input_key == "json_dir"
            mock_execute.assert_called_once_with({"user_prompt": "Summarize the data from all JSON files", "json_dir": "path/to/json/directory"})
            mock_fetch_node.assert_called_once()
            mock_generate_answer_node.assert_called_once()
            mock_create_llm.assert_called_once_with({"model": "test-model", "temperature": 0})