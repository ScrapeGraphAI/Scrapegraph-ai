import urllib.parse
import pytest
from unittest.mock import patch, Mock
from scrapegraphai.docloaders.scrape_do import scrape_do_fetch


def test_scrape_do_fetch_without_proxy():
    """
    Test scrape_do_fetch function using API mode (without proxy).

    This test verifies that:
    1. The function correctly uses the API mode when use_proxy is False.
    2. The correct URL is constructed with the token and encoded target URL.
    3. The function returns the expected response text.
    """
    token = "test_token"
    target_url = "https://example.com"
    encoded_url = urllib.parse.quote(target_url)
    expected_response = "Mocked API response"

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = expected_response
        mock_get.return_value = mock_response

        result = scrape_do_fetch(token, target_url, use_proxy=False)

        expected_url = f"http://api.scrape.do?token={token}&url={encoded_url}"
        mock_get.assert_called_once_with(expected_url)

        assert result == expected_response

