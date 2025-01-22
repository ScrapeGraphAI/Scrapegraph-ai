from pydantic import BaseModel
from scrapegraphai.graphs.json_scraper_graph import JSONScraperGraph
from scrapegraphai.graphs.json_scraper_multi_graph import JSONScraperMultiGraph
from scrapegraphai.nodes import GraphIteratorNode, MergeAnswersNode
from unittest import TestCase
from unittest.mock import MagicMock, patch

class TestJSONScraperMultiGraph(TestCase):
    @patch('scrapegraphai.graphs.json_scraper_multi_graph.BaseGraph')
    @patch.object(JSONScraperMultiGraph, '_create_llm')
    def test_json_scraper_multi_graph(self, mock_create_llm, mock_base_graph):
        """
        Test the initialization and execution of JSONScraperMultiGraph.
        This test covers:
        1. Initialization with various parameters
        2. The _create_graph method
        3. The run method with both empty and non-empty source lists
        4. Handling of the schema parameter
        5. Correct creation of GraphIteratorNode and MergeAnswersNode
        """
        prompt = "Test prompt"
        empty_source = []
        non_empty_source = ["source1", "source2"]
        config = {"llm": {"model": "test_model"}}

        class TestSchema(BaseModel):
            field: str

        # Mock the _create_llm method to return a MagicMock
        mock_create_llm.return_value = MagicMock()

        # Test initialization and _create_graph with empty source
        graph = JSONScraperMultiGraph(prompt, empty_source, config)
        graph._create_graph()

        mock_base_graph.assert_called()
        self.assertIsInstance(graph.graph, MagicMock)

        # Test run method with empty source
        mock_execute = MagicMock(return_value=({}, {}))
        graph.graph.execute = mock_execute
        result = graph.run()

        self.assertEqual(result, "No answer found.")
        mock_execute.assert_called_once_with({"user_prompt": prompt, "jsons": empty_source})

        # Test initialization and _create_graph with non-empty source and schema
        graph = JSONScraperMultiGraph(prompt, non_empty_source, config, schema=TestSchema)
        graph._create_graph()

        # Check if GraphIteratorNode and MergeAnswersNode are created with correct parameters
        calls = mock_base_graph.call_args_list[-1]
        nodes = calls[1]['nodes']
        self.assertEqual(len(nodes), 2)
        self.assertIsInstance(nodes[0], GraphIteratorNode)
        self.assertEqual(nodes[0].node_config['graph_instance'], JSONScraperGraph)
        self.assertIsInstance(nodes[1], MergeAnswersNode)
        self.assertEqual(nodes[1].node_config['schema'], TestSchema)

        # Test run method with non-empty source
        mock_execute = MagicMock(return_value=({"answer": "Test answer"}, {}))
        graph.graph.execute = mock_execute
        result = graph.run()

        self.assertEqual(result, "Test answer")
        mock_execute.assert_called_once_with({"user_prompt": prompt, "jsons": non_empty_source})