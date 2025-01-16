import unittest

from scrapegraphai.graphs.abstract_graph import AbstractGraph
from scrapegraphai.graphs.base_graph import BaseGraph
from scrapegraphai.graphs.smart_scraper_multi_concat_graph import SmartScraperMultiConcatGraph
from unittest import mock

class TestSmartScraperMultiConcatGraph(unittest.TestCase):
    @mock.patch.object(AbstractGraph, '_create_llm')
    @mock.patch.object(BaseGraph, 'execute')
    def test_concat_answers_when_results_less_than_or_equal_to_two(self, mock_execute, mock_create_llm):
        """
        Test that the ConcatAnswersNode is used when the number of results
        is less than or equal to 2.
        """
        # Mock the _create_llm method to return a dummy LLM object
        mock_create_llm.return_value = mock.MagicMock()

        # Mock the config and schema
        mock_config = {"llm": {"model": "openai/gpt-3.5-turbo"}}
        mock_schema = None

        # Mock the BaseGraph execute method to return a predefined result
        mock_execute.return_value = ({"answer": "Concatenated answer"}, {})

        # Create an instance of SmartScraperMultiConcatGraph
        graph = SmartScraperMultiConcatGraph(
            prompt="Test prompt",
            source=["http://example1.com", "http://example2.com"],
            config=mock_config,
            schema=mock_schema
        )

        # Run the graph
        result = graph.run()

        # Assert that the result is the concatenated answer
        self.assertEqual(result, "Concatenated answer")

        # Verify that the execute method was called with the correct inputs
        mock_execute.assert_called_once_with({
            "user_prompt": "Test prompt",
            "urls": ["http://example1.com", "http://example2.com"]
        })

    @mock.patch.object(AbstractGraph, '_create_llm')
    @mock.patch.object(BaseGraph, 'execute')
    def test_merge_answers_when_results_more_than_two(self, mock_execute, mock_create_llm):
        """
        Test that the MergeAnswersNode is used when the number of results
        is more than 2.
        """
        # Mock the _create_llm method to return a dummy LLM object
        mock_create_llm.return_value = mock.MagicMock()

        # Mock the config and schema
        mock_config = {"llm": {"model": "openai/gpt-3.5-turbo"}}
        mock_schema = None

        # Mock the BaseGraph execute method to return a predefined result
        mock_execute.return_value = ({"answer": "Merged answer"}, {})

        # Create an instance of SmartScraperMultiConcatGraph
        graph = SmartScraperMultiConcatGraph(
            prompt="Test prompt",
            source=["http://example1.com", "http://example2.com", "http://example3.com"],
            config=mock_config,
            schema=mock_schema
        )

        # Run the graph
        result = graph.run()

        # Assert that the result is the merged answer
        self.assertEqual(result, "Merged answer")

        # Verify that the execute method was called with the correct inputs
        mock_execute.assert_called_once_with({
            "user_prompt": "Test prompt",
            "urls": ["http://example1.com", "http://example2.com", "http://example3.com"]
        })