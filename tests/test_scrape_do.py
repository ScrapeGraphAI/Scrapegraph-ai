import pytest

from scrapegraphai.docloaders.scrape_do import scrape_do_fetch
from unittest.mock import Mock, patch

class TestScrapeDoFetch:
    @patch('scrapegraphai.docloaders.scrape_do.requests.get')
    @patch('scrapegraphai.docloaders.scrape_do.os.getenv')
    def test_scrape_do_fetch_with_proxy_geocode_and_super_proxy(self, mock_getenv, mock_get):
        """
        Test scrape_do_fetch function with proxy mode, geoCode, and super_proxy enabled.
        This test verifies that the function correctly handles proxy settings,
        geoCode parameter, and super_proxy flag when making a request.
        """
        # Mock environment variable
        mock_getenv.return_value = "proxy.scrape.do:8080"

        # Mock the response
        mock_response = Mock()
        mock_response.text = "Mocked response content"
        mock_get.return_value = mock_response

        # Test parameters
        token = "test_token"
        target_url = "https://example.com"
        use_proxy = True
        geoCode = "US"
        super_proxy = True

        # Call the function
        result = scrape_do_fetch(token, target_url, use_proxy, geoCode, super_proxy)

        # Assertions
        assert result == "Mocked response content"
        mock_get.assert_called_once()
        call_args = mock_get.call_args

        # Check if the URL is correct
        assert call_args[0][0] == target_url

        # Check if proxies are set correctly
        assert call_args[1]['proxies'] == {
            "http": f"http://{token}:@proxy.scrape.do:8080",
            "https": f"http://{token}:@proxy.scrape.do:8080",
        }

        # Check if verify is False
        assert call_args[1]['verify'] is False

        # Check if params are set correctly
        assert call_args[1]['params'] == {"geoCode": "US", "super": "true"}