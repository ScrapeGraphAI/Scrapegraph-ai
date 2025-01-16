import unittest

from scrapegraphai.graphs.csv_scraper_graph import CSVScraperGraph
from scrapegraphai.graphs.csv_scraper_multi_graph import CSVScraperMultiGraph
from unittest.mock import MagicMock, patch

class TestCSVScraperMultiGraph(unittest.TestCase):
    def test_create_graph_structure_and_run(self):
        """
        Test if the CSVScraperMultiGraph creates the correct graph structure
        with GraphIteratorNode and MergeAnswersNode, initializes properly,
        and executes the run method correctly.
        """
        prompt = "Test prompt"
        source = ["url1", "url2"]
        config = {
            "llm": {
                "model": "test-model",
                "model_provider": "openai",
                "temperature": 0  # Adding temperature to match the actual implementation
            },
            "embedder": {"model": "test-embedder"},
            "headless": True,
            "verbose": False,
            "model_token": 1000
        }

        with patch('scrapegraphai.graphs.csv_scraper_multi_graph.GraphIteratorNode') as mock_iterator_node, \
             patch('scrapegraphai.graphs.csv_scraper_multi_graph.MergeAnswersNode') as mock_merge_node, \
             patch('scrapegraphai.graphs.csv_scraper_multi_graph.BaseGraph') as mock_base_graph, \
             patch('scrapegraphai.graphs.abstract_graph.AbstractGraph._create_llm') as mock_create_llm:

            # Mock the _create_llm method to return a MagicMock
            mock_llm = MagicMock()
            mock_create_llm.return_value = mock_llm

            csv_scraper_multi_graph = CSVScraperMultiGraph(prompt, source, config)

            # Check if GraphIteratorNode is created with correct parameters
            mock_iterator_node.assert_called_once_with(
                input="user_prompt & jsons",
                output=["results"],
                node_config={
                    "graph_instance": CSVScraperGraph,
                    "scraper_config": csv_scraper_multi_graph.copy_config,
                }
            )

            # Check if MergeAnswersNode is created with correct parameters
            mock_merge_node.assert_called_once_with(
                input="user_prompt & results",
                output=["answer"],
                node_config={"llm_model": mock_llm, "schema": csv_scraper_multi_graph.copy_schema}
            )

            # Check if BaseGraph is created with correct structure
            mock_base_graph.assert_called_once()
            graph_args = mock_base_graph.call_args[1]
            self.assertEqual(len(graph_args['nodes']), 2)
            self.assertEqual(len(graph_args['edges']), 1)
            self.assertEqual(graph_args['entry_point'], mock_iterator_node.return_value)
            self.assertEqual(graph_args['graph_name'], "CSVScraperMultiGraph")

            # Check if the graph attribute is set correctly
            self.assertIsInstance(csv_scraper_multi_graph.graph, MagicMock)

            # Check if the prompt and source are set correctly
            self.assertEqual(csv_scraper_multi_graph.prompt, prompt)
            self.assertEqual(csv_scraper_multi_graph.source, source)

            # Check if the config is copied correctly
            self.assertDictEqual(csv_scraper_multi_graph.copy_config, config)

            # Test the run method
            mock_execute = MagicMock(return_value=({"answer": "Test answer"}, {}))
            csv_scraper_multi_graph.graph.execute = mock_execute

            result = csv_scraper_multi_graph.run()

            mock_execute.assert_called_once_with({"user_prompt": prompt, "jsons": source})
            self.assertEqual(result, "Test answer")

            # Test the case when no answer is found
            mock_execute.return_value = ({}, {})
            result = csv_scraper_multi_graph.run()
            self.assertEqual(result, "No answer found.")