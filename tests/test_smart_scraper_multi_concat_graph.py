import unittest

from scrapegraphai.graphs.base_graph import BaseGraph
from scrapegraphai.graphs.smart_scraper_multi_concat_graph import SmartScraperMultiConcatGraph
from unittest import mock

class TestSmartScraperMultiConcatGraph(unittest.TestCase):
    @mock.patch('scrapegraphai.graphs.abstract_graph.init_chat_model')
    @mock.patch.object(BaseGraph, 'execute')
    def test_concat_answers_when_results_less_than_or_equal_to_two(self, mock_execute, mock_init_chat_model):
        """
        Test that the ConcatAnswersNode is used when the number of results
        is less than or equal to 2.
        """
        # Mock the config and schema
        mock_config = {"llm": {"model": "openai/gpt-3.5-turbo"}}
        mock_schema = None

        # Mock the OpenAI client
        mock_openai_client = mock.MagicMock()
        mock_init_chat_model.return_value = mock_openai_client

        # Create an instance of SmartScraperMultiConcatGraph
        graph = SmartScraperMultiConcatGraph(
            prompt="Test prompt",
            source=["http://example1.com", "http://example2.com"],
            config=mock_config,
            schema=mock_schema
        )

        # Mock the BaseGraph execute method to return a predefined result
        mock_execute.return_value = ({"answer": "Concatenated answer"}, {})

        # Run the graph
        result = graph.run()

        # Assert that the result is the concatenated answer
        self.assertEqual(result, "Concatenated answer")

        # Verify that the execute method was called with the correct inputs
        mock_execute.assert_called_once_with({
            "user_prompt": "Test prompt",
            "urls": ["http://example1.com", "http://example2.com"]
        })

    @mock.patch('scrapegraphai.graphs.abstract_graph.init_chat_model')
    @mock.patch.object(BaseGraph, 'execute')
    def test_merge_answers_when_results_more_than_two(self, mock_execute, mock_init_chat_model):
        """
        Test that the MergeAnswersNode is used when the number of results
        is more than 2.
        """
        # Mock the config and schema
        mock_config = {"llm": {"model": "openai/gpt-3.5-turbo"}}
        mock_schema = None

        # Mock the OpenAI client
        mock_openai_client = mock.MagicMock()
        mock_init_chat_model.return_value = mock_openai_client

        # Create an instance of SmartScraperMultiConcatGraph
        graph = SmartScraperMultiConcatGraph(
            prompt="Test prompt",
            source=["http://example1.com", "http://example2.com", "http://example3.com"],
            config=mock_config,
            schema=mock_schema
        )

        # Mock the BaseGraph execute method to return a predefined result
        mock_execute.return_value = ({"answer": "Merged answer"}, {})

        # Run the graph
        result = graph.run()

        # Assert that the result is the merged answer
        self.assertEqual(result, "Merged answer")

        # Verify that the execute method was called with the correct inputs
        mock_execute.assert_called_once_with({
            "user_prompt": "Test prompt",
            "urls": ["http://example1.com", "http://example2.com", "http://example3.com"]
        })