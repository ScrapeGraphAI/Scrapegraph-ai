from unittest.mock import MagicMock, patch

import pytest

from scrapegraphai.utils.research_web import (
    SearchConfig,
    SearchConfigError,
    SearchRequestError,
    _search_tavily,
    search_on_web,
)


def test_google_search():
    """Tests search_on_web with Google search engine."""
    results = search_on_web("test query", search_engine="Google", max_results=2)
    assert len(results) == 2
    # You can further assert if the results actually contain 'test query' in the title/snippet using additional libraries


def test_bing_search():
    """Tests search_on_web with Bing search engine."""
    results = search_on_web("test query", search_engine="Bing", max_results=1)
    assert results is not None
    # You can further assert if the results contain '.com' or '.org' in the domain


def test_invalid_search_engine():
    """Tests search_on_web with invalid search engine."""
    with pytest.raises(ValueError):
        search_on_web("test query", search_engine="Yahoo", max_results=5)


def test_max_results():
    """Tests search_on_web with different max_results values."""
    results_5 = search_on_web("test query", max_results=5)
    results_10 = search_on_web("test query", max_results=10)
    assert len(results_5) <= len(results_10)


# --- Tavily search engine tests ---


def test_search_config_accepts_tavily():
    """Tests that SearchConfig accepts 'tavily' as a valid search engine."""
    config = SearchConfig(query="test query", search_engine="tavily")
    assert config.search_engine == "tavily"


def test_search_tavily_success():
    """Tests _search_tavily returns URLs from Tavily search results."""
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [
            {"title": "Result 1", "url": "https://example.com/1", "score": 0.9},
            {"title": "Result 2", "url": "https://example.com/2", "score": 0.8},
        ]
    }
    mock_tavily_module = MagicMock()
    mock_tavily_module.TavilyClient.return_value = mock_client

    with patch.dict("sys.modules", {"tavily": mock_tavily_module}):
        results = _search_tavily("test query", max_results=2, api_key="tvly-test-key")

    assert results == ["https://example.com/1", "https://example.com/2"]
    mock_tavily_module.TavilyClient.assert_called_once_with(api_key="tvly-test-key")
    mock_client.search.assert_called_once_with(query="test query", max_results=2)


def test_search_tavily_missing_api_key():
    """Tests _search_tavily raises SearchConfigError when API key is missing."""
    with pytest.raises(SearchConfigError, match="Tavily API key is required"):
        _search_tavily("test query", max_results=5, api_key=None)


def test_search_tavily_empty_api_key():
    """Tests _search_tavily raises SearchConfigError when API key is empty string."""
    with pytest.raises(SearchConfigError, match="Tavily API key is required"):
        _search_tavily("test query", max_results=5, api_key="")


def test_search_tavily_api_error():
    """Tests _search_tavily raises SearchRequestError on API failure."""
    mock_client = MagicMock()
    mock_client.search.side_effect = Exception("API rate limit exceeded")
    mock_tavily_module = MagicMock()
    mock_tavily_module.TavilyClient.return_value = mock_client

    with patch.dict("sys.modules", {"tavily": mock_tavily_module}):
        with pytest.raises(SearchRequestError, match="Tavily search failed"):
            _search_tavily("test query", max_results=5, api_key="tvly-test-key")


def test_search_tavily_empty_results():
    """Tests _search_tavily returns empty list when no results found."""
    mock_client = MagicMock()
    mock_client.search.return_value = {"results": []}
    mock_tavily_module = MagicMock()
    mock_tavily_module.TavilyClient.return_value = mock_client

    with patch.dict("sys.modules", {"tavily": mock_tavily_module}):
        results = _search_tavily("test query", max_results=5, api_key="tvly-test-key")

    assert results == []


@patch("scrapegraphai.utils.research_web._search_tavily")
def test_search_on_web_tavily_integration(mock_search_tavily):
    """Tests search_on_web dispatches to tavily engine correctly."""
    mock_search_tavily.return_value = [
        "https://example.com/1",
        "https://example.com/2",
    ]

    results = search_on_web(
        "test query",
        search_engine="tavily",
        max_results=2,
        tavily_api_key="tvly-test-key",
    )

    assert results == ["https://example.com/1", "https://example.com/2"]
    mock_search_tavily.assert_called_once()
