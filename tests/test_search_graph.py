import unittest

from scrapegraphai.graphs.search_graph import SearchGraph
from unittest.mock import MagicMock, patch

class TestSearchGraph(unittest.TestCase):
    @patch('scrapegraphai.graphs.abstract_graph.init_chat_model')
    @patch('scrapegraphai.graphs.base_graph.BaseGraph.execute')
    def test_get_considered_urls(self, mock_execute, mock_init_chat_model):
        """
        Test that get_considered_urls() returns the correct list of URLs after running the graph.
        This test mocks the OpenAI client and the graph execution to avoid actual API calls.
        """
        # Mock the OpenAI client
        mock_init_chat_model.return_value = MagicMock()

        # Mock the configuration
        config = {
            "llm": {"model": "openai/gpt-3.5-turbo"},
            "max_results": 2
        }

        # Mock the execute method of BaseGraph to set the final_state
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

        # Verify that init_chat_model was called
        mock_init_chat_model.assert_called_once()