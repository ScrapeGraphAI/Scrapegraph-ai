import unittest

from pydantic import BaseModel
from scrapegraphai.graphs.base_graph import BaseGraph
from scrapegraphai.graphs.xml_scraper_multi_graph import XMLScraperMultiGraph
from unittest.mock import MagicMock, call, patch

class TestXMLScraperMultiGraph(unittest.TestCase):
    def setUp(self):
        self.custom_config = {
            "llm": {"model": "openai/gpt-3.5-turbo"},
            "embedder": {"model": "custom_embedder"},
        }
        self.prompt = "Test prompt"
        self.source = ["http://example.com"]

    def test_initialization(self):
        """
        Test that XMLScraperMultiGraph initializes correctly with custom configuration and schema.
        """
        class CustomSchema(BaseModel):
            answer: str

        with patch('scrapegraphai.graphs.xml_scraper_multi_graph.AbstractGraph.__init__') as mock_init:
            graph = XMLScraperMultiGraph(
                prompt=self.prompt,
                source=self.source,
                config=self.custom_config,
                schema=CustomSchema
            )

            mock_init.assert_called_once_with(self.prompt, self.custom_config, self.source, CustomSchema)
            self.assertEqual(graph.copy_config, self.custom_config)
            self.assertEqual(graph.copy_schema, CustomSchema)

    def test_create_graph(self):
        """
        Test that the _create_graph method creates the correct graph structure.
        """
        with patch('scrapegraphai.graphs.xml_scraper_multi_graph.AbstractGraph.__init__', return_value=None):
            graph = XMLScraperMultiGraph(
                prompt=self.prompt,
                source=self.source,
                config=self.custom_config
            )
            graph.llm_model = MagicMock()

            with patch('scrapegraphai.graphs.xml_scraper_multi_graph.BaseGraph') as MockBaseGraph, \
                 patch('scrapegraphai.graphs.xml_scraper_multi_graph.GraphIteratorNode') as MockGraphIteratorNode, \
                 patch('scrapegraphai.graphs.xml_scraper_multi_graph.MergeAnswersNode') as MockMergeAnswersNode:

                result = graph._create_graph()

                MockGraphIteratorNode.assert_called_once()
                MockMergeAnswersNode.assert_called_once()
                MockBaseGraph.assert_called_once()

                # Check if BaseGraph was called with the correct arguments
                self.assertEqual(MockBaseGraph.call_args[1]['graph_name'], "XMLScraperMultiGraph")

    def test_run_method(self):
        """
        Test the run method of XMLScraperMultiGraph.
        """
        with patch('scrapegraphai.graphs.xml_scraper_multi_graph.AbstractGraph.__init__', return_value=None):
            graph = XMLScraperMultiGraph(
                prompt=self.prompt,
                source=self.source,
                config=self.custom_config
            )
            # Manually set prompt and source attributes
            graph.prompt = self.prompt
            graph.source = self.source
            graph.graph = MagicMock()
            graph.graph.execute.return_value = ({"answer": "Test answer"}, {})

            result = graph.run()

            self.assertEqual(result, "Test answer")
            graph.graph.execute.assert_called_once_with({"user_prompt": self.prompt, "xmls": self.source})