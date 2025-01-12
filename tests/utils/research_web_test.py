import json
import pytest
import re

from bs4 import BeautifulSoup
from requests.exceptions import Timeout
from scrapegraphai.utils.research_web import _search_bing, _search_searxng, filter_pdf_links, format_proxy, search_on_web, search_on_web  # Replace with actual path to your file
from typing import List
from unittest.mock import MagicMock, patch

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

def test_filter_pdf_links():
    """Tests the filter_pdf_links function to ensure it removes PDF links."""
    test_links: List[str] = [
        "http://example.com/document.pdf",
        "https://example.org/page",
        "http://test.com/file.PDF",  # Testing case insensitivity
        "https://another.com/resource",
        "ftp://files.net/document.pdf"
    ]

    filtered_links = filter_pdf_links(test_links)

    assert len(filtered_links) == 2
    assert "http://example.com/document.pdf" not in filtered_links
    assert "http://test.com/file.PDF" not in filtered_links
    assert "ftp://files.net/document.pdf" not in filtered_links
    assert "https://example.org/page" in filtered_links
    assert "https://another.com/resource" in filtered_links

def test_empty_query():
    """Tests search_on_web with an empty query string."""
    with pytest.raises(ValueError, match="Query must be a non-empty string"):
        search_on_web("", search_engine="Google", max_results=5)

def test_duckduckgo_search():
    """Tests search_on_web with DuckDuckGo search engine."""
    mock_results = "Result 1: https://example.com, Result 2: https://test.org"

    # Create a mock DuckDuckGoSearchResults object
    mock_duckduckgo = MagicMock()
    mock_duckduckgo.run.return_value = mock_results

    # Patch the DuckDuckGoSearchResults class
    with patch('scrapegraphai.utils.research_web.DuckDuckGoSearchResults', return_value=mock_duckduckgo):
        results = search_on_web("test query", search_engine="duckduckgo", max_results=2)

    assert len(results) == 2
    assert all(url.startswith('http') for url in results)
    assert 'https://example.com' in results
    assert 'https://test.org' in results

@patch('scrapegraphai.utils.research_web.requests.post')
def test_search_serper(mock_post):
    # Prepare mock response
    mock_response = {
        "organic": [
            {"link": "https://example1.com"},
            {"link": "https://example2.com"},
            {"link": "https://example3.com"}
        ]
    }
    mock_post.return_value.json.return_value = mock_response
    mock_post.return_value.raise_for_status.return_value = None

    # Call the function
    results = _search_serper("test query", 3, "fake_api_key", 10)

    # Assertions
    assert len(results) == 3
    assert results == ["https://example1.com", "https://example2.com", "https://example3.com"]

    # Verify the API call
    mock_post.assert_called_once_with(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": "fake_api_key", "Content-Type": "application/json"},
        json={"q": "test query", "num": 3},
        timeout=10
    )

@pytest.mark.parametrize("proxy_input, expected_proxy", [
    ({"server": "127.0.0.1:8080", "username": "user", "password": "pass"}, "http://user:pass@127.0.0.1:8080"),
    ("http://proxy.example.com:8080", "http://proxy.example.com:8080")
])
@patch('scrapegraphai.utils.research_web.google_search')
def test_search_on_web_with_proxy(mock_google_search, proxy_input, expected_proxy):
    """Test search_on_web function with proxy configuration"""

    # Mock the google_search function to return a list of URLs
    mock_google_search.return_value = ["https://example.com", "https://test.com"]

    # Call search_on_web with a proxy
    results = search_on_web("test query", search_engine="Google", max_results=2, proxy=proxy_input)

    # Assert that the results are as expected
    assert results == ["https://example.com", "https://test.com"]

    # Verify that google_search was called with the correct proxy
    mock_google_search.assert_called_once()
    call_args = mock_google_search.call_args[1]
    assert call_args['proxy'] == expected_proxy

    # Verify other parameters
    assert call_args['query'] == "test query"
    assert call_args['num_results'] == 2

@pytest.mark.parametrize("region, language", [
    ("mx", "es"),
    ("fr", "fr"),
    (None, "de"),
    ("uk", None),
])
@patch('scrapegraphai.utils.research_web.google_search')
def test_search_on_web_with_region_and_language(mock_google_search, region, language):
    """Test search_on_web function with region and language parameters"""

    # Mock the google_search function to return a list of URLs
    mock_google_search.return_value = ["https://example.com", "https://test.com"]

    # Call search_on_web with region and language
    results = search_on_web("test query", search_engine="Google", max_results=2, region=region, language=language)

    # Assert that the results are as expected
    assert results == ["https://example.com", "https://test.com"]

    # Verify that google_search was called with the correct parameters
    mock_google_search.assert_called_once()
    call_args = mock_google_search.call_args[1]
    assert call_args['query'] == "test query"
    assert call_args['num_results'] == 2

    if region:
        assert call_args['region'] == region
    if language:
        assert call_args['lang'] == language

    # Verify that region and language are only in call_args if they were provided
    assert ('region' in call_args) == (region is not None)
    assert ('lang' in call_args) == (language is not None)

@patch('scrapegraphai.utils.research_web.requests.get')
def test_search_searxng(mock_get):
    # Prepare mock response
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {"url": "https://example1.com"},
            {"url": "https://example2.com"},
            {"url": "https://example3.com"}
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Call the function
    results = _search_searxng("test query", 3, 8080, 10)

    # Assertions
    assert len(results) == 3
    assert results == ["https://example1.com", "https://example2.com", "https://example3.com"]

    # Verify the API call
    mock_get.assert_called_once_with(
        "http://localhost:8080/search",
        params={
            "q": "test query",
            "format": "json",
            "engines": "google,duckduckgo,brave,qwant,bing"
        },
        timeout=10
    )

@patch('scrapegraphai.utils.research_web.requests.get')
@patch('scrapegraphai.utils.research_web.BeautifulSoup')
def test_search_bing(mock_bs, mock_get):
    # Prepare mock response
    mock_response = MagicMock()
    mock_response.text = "<html><body></body></html>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Prepare mock BeautifulSoup
    mock_soup = MagicMock()
    mock_bs.return_value = mock_soup

    # Mock find_all method to return a list of mock results
    mock_result1 = MagicMock()
    mock_result1.find.return_value = {"href": "https://example1.com"}
    mock_result2 = MagicMock()
    mock_result2.find.return_value = {"href": "https://example2.com"}
    mock_soup.find_all.return_value = [mock_result1, mock_result2]

    # Call the function
    results = _search_bing("test query", 2, 10)

    # Assertions
    assert len(results) == 2
    assert results == ["https://example1.com", "https://example2.com"]

    # Verify the API call
    mock_get.assert_called_once_with(
        "https://www.bing.com/search?q=test query",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
        timeout=10,
        proxies=None
    )

    # Verify BeautifulSoup call
    mock_bs.assert_called_once_with(mock_response.text, "html.parser")

    # Verify find_all call
    mock_soup.find_all.assert_called_once_with("li", class_="b_algo", limit=2)

@pytest.mark.parametrize("invalid_proxy", [
    {"server": "127.0.0.1:8080", "username": "user"},  # Missing password
    {"username": "user", "password": "pass"},  # Missing server
    {"server": "127.0.0.1:8080"},  # Missing username and password
    42,  # Invalid type
])
@patch('scrapegraphai.utils.research_web.google_search')
def test_search_on_web_with_invalid_proxy(mock_google_search, invalid_proxy):
    """Test search_on_web function with invalid proxy configurations"""

    with pytest.raises(ValueError) as exc_info:
        search_on_web("test query", search_engine="Google", max_results=2, proxy=invalid_proxy)

    if isinstance(invalid_proxy, dict):
        assert str(exc_info.value) == "Proxy dictionary is missing required fields."
    else:
        assert str(exc_info.value) == "Proxy should be a dictionary or a string."

    # Verify that google_search was not called
    mock_google_search.assert_not_called()

@patch('scrapegraphai.utils.research_web.google_search')
def test_search_on_web_timeout(mock_google_search):
    """Test search_on_web function when a timeout occurs"""

    # Configure the mock to raise a Timeout exception
    mock_google_search.side_effect = Timeout("Request timed out")

    # Call search_on_web and expect a TimeoutError
    with pytest.raises(TimeoutError) as exc_info:
        search_on_web("test query", search_engine="Google", max_results=2, timeout=5)

    # Verify the error message
    assert str(exc_info.value) == "Search request timed out after 5 seconds"

    # Verify that google_search was called with the correct parameters
    mock_google_search.assert_called_once_with("test query", num_results=2, proxy=None)