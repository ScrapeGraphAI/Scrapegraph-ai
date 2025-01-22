import unittest

from scrapegraphai.graphs.abstract_graph import AbstractGraph
from scrapegraphai.graphs.document_scraper_multi_graph import DocumentScraperMultiGraph
from unittest.mock import MagicMock, patch

class TestDocumentScraperMultiGraph(unittest.TestCase):
    def test_no_answer_found(self):
        """
        Test that DocumentScraperMultiGraph returns 'No answer found.' when the graph execution
        doesn't produce an answer.
        """
        prompt = "What is the meaning of life?"
        sources = ["http://example.com/page1", "http://example.com/page2"]
        config = {"llm_model": {"model": "openai/gpt-3.5-turbo"}}

        with patch.object(AbstractGraph, '__init__', return_value=None):
            with patch.object(DocumentScraperMultiGraph, '_create_graph') as mock_create_graph:
                mock_graph = MagicMock()
                mock_graph.execute.return_value = ({}, {})  # Empty final_state and execution_info
                mock_create_graph.return_value = mock_graph

                scraper = DocumentScraperMultiGraph(prompt, sources, config)
                scraper.prompt = prompt  # Manually set the prompt attribute
                scraper.source = sources  # Manually set the source attribute
                scraper.graph = mock_graph  # Set the graph attribute to our mock

                result = scraper.run()

        self.assertEqual(result, "No answer found.")