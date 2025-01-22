from scrapegraphai.graphs.abstract_graph import AbstractGraph
from scrapegraphai.graphs.screenshot_scraper_graph import ScreenshotScraperGraph
from unittest import TestCase
from unittest.mock import MagicMock, patch

class TestScreenshotScraperGraph(TestCase):
    @patch('scrapegraphai.graphs.screenshot_scraper_graph.FetchScreenNode')
    @patch('scrapegraphai.graphs.screenshot_scraper_graph.GenerateAnswerFromImageNode')
    @patch('scrapegraphai.graphs.screenshot_scraper_graph.BaseGraph')
    @patch.object(AbstractGraph, '_create_llm')
    def test_screenshot_scraper_graph_run(self, mock_create_llm, mock_base_graph, mock_generate_answer, mock_fetch_screen):
        """
        Test the run method of ScreenshotScraperGraph.
        This test checks if the graph is created correctly and executes as expected.
        It also verifies that the _create_llm method is called with the correct parameters.
        """
        # Mock the nodes, BaseGraph, and _create_llm
        mock_fetch_screen.return_value = MagicMock()
        mock_generate_answer.return_value = MagicMock()
        mock_base_graph.return_value = MagicMock()
        mock_create_llm.return_value = MagicMock()

        # Create a ScreenshotScraperGraph instance
        prompt = "What's in this image?"
        source = "https://example.com"
        config = {
            "llm": {
                "temperature": 0.7,
                "model": "gpt-3.5-turbo"  # Add the model key
            },
            "api_key": "test_key"
        }
        graph = ScreenshotScraperGraph(prompt, source, config)

        # Mock the BaseGraph execute method
        mock_base_graph.return_value.execute.return_value = ({"answer": "This is a test answer"}, {})

        # Run the graph
        result = graph.run()

        # Assert that the execute method was called with the correct input
        mock_base_graph.return_value.execute.assert_called_once_with({"user_prompt": prompt})

        # Assert that the result is correct
        self.assertEqual(result, "This is a test answer")

        # Assert that the nodes were created with the correct parameters
        mock_fetch_screen.assert_called_once_with(
            input="url", output=["screenshots"], node_config={"link": source}
        )
        mock_generate_answer.assert_called_once_with(
            input="screenshots", output=["answer"], node_config={"config": config}
        )

        # Assert that BaseGraph was called with the correct parameters
        mock_base_graph.assert_called_once()
        _, kwargs = mock_base_graph.call_args
        self.assertEqual(len(kwargs['nodes']), 2)
        self.assertEqual(len(kwargs['edges']), 1)
        self.assertEqual(kwargs['entry_point'], mock_fetch_screen.return_value)
        self.assertEqual(kwargs['graph_name'], 'ScreenshotScraperGraph')

        # Assert that _create_llm was called with the correct parameters
        mock_create_llm.assert_called_once_with(config["llm"])