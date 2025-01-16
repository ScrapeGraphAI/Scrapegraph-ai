from scrapegraphai.graphs.json_scraper_multi_graph import JSONScraperMultiGraph
from unittest import TestCase
from unittest.mock import MagicMock, patch

class TestJSONScraperMultiGraph(TestCase):
    def test_empty_source_list(self):
        """
        Test that JSONScraperMultiGraph handles an empty source list gracefully.
        This test ensures that the graph is created correctly with an empty list of sources
        and returns a default message when run with no results.
        """
        prompt = "Test prompt"
        empty_source = []
        config = {
            "llm": {
                "model": "test_model",
                "model_provider": "test_provider"
            }
        }

        with patch('scrapegraphai.graphs.json_scraper_multi_graph.BaseGraph') as mock_base_graph, \
             patch('scrapegraphai.graphs.json_scraper_multi_graph.GraphIteratorNode') as mock_graph_iterator_node, \
             patch('scrapegraphai.graphs.json_scraper_multi_graph.MergeAnswersNode') as mock_merge_answers_node, \
             patch('scrapegraphai.graphs.abstract_graph.AbstractGraph._create_llm') as mock_create_llm:

            # Create mock instances
            mock_graph_instance = MagicMock()
            mock_base_graph.return_value = mock_graph_instance

            # Mock the execute method to return a dictionary with no answer
            mock_graph_instance.execute.return_value = ({"answer": "No answer found."}, {})

            # Mock the _create_llm method
            mock_create_llm.return_value = MagicMock()

            # Initialize the JSONScraperMultiGraph
            graph = JSONScraperMultiGraph(prompt, empty_source, config)

            # Run the graph
            result = graph.run()

        # Assert that the graph was created with the correct nodes
        mock_graph_iterator_node.assert_called_once()
        mock_merge_answers_node.assert_called_once()

        # Assert that BaseGraph was initialized with the correct parameters
        mock_base_graph.assert_called_once()
        _, kwargs = mock_base_graph.call_args
        self.assertEqual(len(kwargs['nodes']), 2)
        self.assertEqual(len(kwargs['edges']), 1)

        # Assert that the execute method was called with the correct inputs
        mock_graph_instance.execute.assert_called_once_with({"user_prompt": prompt, "jsons": empty_source})

        # Assert the result
        self.assertEqual(result, "No answer found.")