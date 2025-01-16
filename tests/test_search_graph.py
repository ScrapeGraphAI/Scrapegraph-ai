import os
import unittest

from scrapegraphai.graphs.search_graph import SearchGraph
from unittest.mock import MagicMock, patch

class TestSearchGraph(unittest.TestCase):
    @patch.dict(os.environ, {"OPENAI_API_KEY": "dummy_api_key"})
    @patch('scrapegraphai.graphs.base_graph.BaseGraph.execute')
    def test_get_considered_urls(self, mock_execute):
        """
        Test that get_considered_urls() returns the correct list of URLs after running the graph.
        This test mocks the OpenAI API key and the graph execution to simulate the behavior.
        """
        # Mock the configuration
        config = {
            "llm": {"model": "openai/gpt-3.5-turbo"},
            "max_results": 2
        }

        # Mock the execute method to return a predefined final state
        mock_execute.return_value = (
            {"urls": ["https://example1.com", "https://example2.com"], "answer": "Chioggia is famous for its beaches."},
            {}
        )

        # Create a SearchGraph instance
        search_graph = SearchGraph("What is Chioggia famous for?", config)

        # Run the graph
        result = search_graph.run()

        # Check if the result is correct
        self.assertEqual(result, "Chioggia is famous for its beaches.")

        # Check if get_considered_urls returns the correct list
        considered_urls = search_graph.get_considered_urls()
        self.assertEqual(considered_urls, ["https://example1.com", "https://example2.com"])

        # Verify that the execute method was called
        mock_execute.assert_called_once()