from unittest.mock import MagicMock, patch

import pytest

from scrapegraphai.graphs.search_graph import SearchGraph, SearchGraphEmptyAnswerError


class TestSearchGraph:
    """Test class for SearchGraph"""

    @pytest.mark.parametrize(
        "urls",
        [["https://example.com", "https://test.com"], [], ["https://single-url.com"]],
    )
    @patch("scrapegraphai.graphs.search_graph.BaseGraph")
    @patch("scrapegraphai.graphs.abstract_graph.AbstractGraph._create_llm")
    def test_get_considered_urls(self, mock_create_llm, mock_base_graph, urls):
        """
        Test that get_considered_urls returns the correct list of URLs
        considered during the search process.
        """
        # Arrange
        prompt = "Test prompt"
        config = {"llm": {"model": "test-model"}}

        # Mock the _create_llm method to return a MagicMock
        mock_create_llm.return_value = MagicMock()

        # Mock the execute method to set the final_state
        mock_base_graph.return_value.execute.return_value = ({"urls": urls, "answer": "ok"}, {})

        # Act
        search_graph = SearchGraph(prompt, config)
        search_graph.run()

        # Assert
        assert search_graph.get_considered_urls() == urls

    @patch("scrapegraphai.graphs.search_graph.BaseGraph")
    @patch("scrapegraphai.graphs.abstract_graph.AbstractGraph._create_llm")
    def test_run_no_answer_found(self, mock_create_llm, mock_base_graph):
        """
        Test that the run() method returns "No answer found." when the final state
        doesn't contain an "answer" key.
        """
        # Arrange
        prompt = "Test prompt"
        config = {"llm": {"model": "test-model"}}

        # Mock the _create_llm method to return a MagicMock
        mock_create_llm.return_value = MagicMock()

        # Mock the execute method to set the final_state without an "answer" key
        mock_base_graph.return_value.execute.return_value = ({"urls": []}, {})

        # Act / Assert: silent "No answer found." is now a clear exception
        search_graph = SearchGraph(prompt, config)
        with pytest.raises(SearchGraphEmptyAnswerError) as exc_info:
            search_graph.run()
        assert "no URLs were considered" in str(exc_info.value)
        assert exc_info.value.considered_urls == []

    @patch("scrapegraphai.graphs.search_graph.BaseGraph")
    @patch("scrapegraphai.graphs.abstract_graph.AbstractGraph._create_llm")
    def test_run_empty_answer_with_urls_raises(self, mock_create_llm, mock_base_graph):
        """
        When URLs were considered but the scraper/LLM produced no answer,
        run() must surface a clear error (not a silent "No answer found.").
        """
        prompt = "Test prompt"
        config = {"llm": {"model": "test-model"}}
        urls = ["https://a.com", "https://b.com"]

        mock_create_llm.return_value = MagicMock()
        mock_base_graph.return_value.execute.return_value = ({"urls": urls}, {})

        search_graph = SearchGraph(prompt, config)
        with pytest.raises(SearchGraphEmptyAnswerError) as exc_info:
            search_graph.run()
        assert exc_info.value.considered_urls == urls
        assert "2 URL(s)" in str(exc_info.value)

    @patch("scrapegraphai.graphs.search_graph.SearchInternetNode")
    @patch("scrapegraphai.graphs.search_graph.GraphIteratorNode")
    @patch("scrapegraphai.graphs.search_graph.MergeAnswersNode")
    @patch("scrapegraphai.graphs.search_graph.BaseGraph")
    @patch("scrapegraphai.graphs.abstract_graph.AbstractGraph._create_llm")
    def test_max_results_config(
        self,
        mock_create_llm,
        mock_base_graph,
        mock_merge_answers,
        mock_graph_iterator,
        mock_search_internet,
    ):
        """
        Test that the max_results parameter from the config is correctly passed to the SearchInternetNode.
        """
        # Arrange
        prompt = "Test prompt"
        max_results = 5
        config = {"llm": {"model": "test-model"}, "max_results": max_results}

        # Act
        SearchGraph(prompt, config)

        # Assert
        mock_search_internet.assert_called_once()
        call_args = mock_search_internet.call_args
        assert call_args.kwargs["node_config"]["max_results"] == max_results

    @patch("scrapegraphai.graphs.search_graph.SearchInternetNode")
    @patch("scrapegraphai.graphs.search_graph.GraphIteratorNode")
    @patch("scrapegraphai.graphs.search_graph.MergeAnswersNode")
    @patch("scrapegraphai.graphs.search_graph.BaseGraph")
    @patch("scrapegraphai.graphs.abstract_graph.AbstractGraph._create_llm")
    def test_custom_search_engine_config(
        self,
        mock_create_llm,
        mock_base_graph,
        mock_merge_answers,
        mock_graph_iterator,
        mock_search_internet,
    ):
        """
        Test that the custom search_engine parameter from the config is correctly passed to the SearchInternetNode.
        """
        # Arrange
        prompt = "Test prompt"
        custom_search_engine = "custom_engine"
        config = {"llm": {"model": "test-model"}, "search_engine": custom_search_engine}

        # Act
        SearchGraph(prompt, config)

        # Assert
        mock_search_internet.assert_called_once()
        call_args = mock_search_internet.call_args
        assert call_args.kwargs["node_config"]["search_engine"] == custom_search_engine
