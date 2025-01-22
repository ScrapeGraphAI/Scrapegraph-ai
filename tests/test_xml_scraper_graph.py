import unittest

from scrapegraphai.graphs.xml_scraper_graph import XMLScraperGraph
from unittest.mock import MagicMock, patch

class TestXMLScraperGraph(unittest.TestCase):
    @patch('scrapegraphai.graphs.xml_scraper_graph.BaseGraph')
    @patch.object(XMLScraperGraph, '_create_llm')
    def test_xml_scraper_graph_with_directory_source(self, mock_create_llm, MockBaseGraph):
        """
        Test XMLScraperGraph with a directory source containing multiple XML files.
        This test checks if the graph correctly handles a directory input and processes multiple XML files.
        It also verifies that the _create_llm method is called and that the input_key is set correctly.
        """
        # Mock the _create_llm method to return a mock LLM
        mock_llm = MagicMock()
        mock_create_llm.return_value = mock_llm

        # Mock the BaseGraph's execute method
        mock_execute = MagicMock(return_value=({
            "answer": "Processed multiple XML files from directory"
        }, {}))
        MockBaseGraph.return_value.execute = mock_execute

        # Create a mock directory path
        mock_dir = "/path/to/xml/directory"

        # Create an instance of XMLScraperGraph with a directory source
        xml_scraper = XMLScraperGraph(
            prompt="Summarize the content of all XML files",
            source=mock_dir,
            config={"llm": {"model": "mock_model"}}
        )

        # Assert that _create_llm was called
        mock_create_llm.assert_called_once()

        # Assert that the input_key is set to "xml_dir" for directory source
        self.assertEqual(xml_scraper.input_key, "xml_dir")

        # Run the graph
        result = xml_scraper.run()

        # Assert that the execute method was called with the correct inputs
        mock_execute.assert_called_once_with({
            "user_prompt": "Summarize the content of all XML files",
            "xml_dir": mock_dir
        })

        # Assert that the result is as expected
        self.assertEqual(result, "Processed multiple XML files from directory")