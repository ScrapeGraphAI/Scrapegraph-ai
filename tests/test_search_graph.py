import pytest

from scrapegraphai.graphs.search_graph import SearchGraph
from unittest.mock import MagicMock, patch

class TestSearchGraph:
    """Test class for SearchGraph"""

    @pytest.mark.parametrize("urls", [
        ["https://example.com", "https://test.com"],
        [],
        ["https://single-url.com"]
    ])
    @patch('scrapegraphai.graphs.search_graph.BaseGraph')
    @patch('scrapegraphai.graphs.abstract_graph.AbstractGraph._create_llm')
    def test_get_considered_urls(self, mock_create_llm, mock_base_graph, urls):
        """
        Test that get_considered_urls returns the correct list of URLs
        considered during the search process.
        """
        # Arrange
        prompt = "Test prompt"
        config = {"llm": {"model": "test-model"}}

        # Mock the _create_llm method to return a MagicMock
        mock_create_llm.return_value = MagicMock()

        # Mock the execute method to set the final_state
        mock_base_graph.return_value.execute.return_value = ({"urls": urls}, {})

        # Act
        search_graph = SearchGraph(prompt, config)
        search_graph.run()

        # Assert
        assert search_graph.get_considered_urls() == urls