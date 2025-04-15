import urllib.parse
from unittest.mock import Mock, patch

import pytest

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


def test_scrape_do_fetch_with_proxy_no_geo():
    """
    Test scrape_do_fetch function using proxy mode without geoCode.
    This test verifies that:
        - The function constructs the correct proxy URL with the default proxy endpoint.
        - The function calls requests.get with the proper proxies, verify flag and empty params.
        - The function returns the expected response text.
    """
    token = "test_token"
    target_url = "https://example.org"
    expected_response = "Mocked proxy response"

    # The default proxy endpoint is used as defined in the function
    expected_proxy_scrape_do_url = "proxy.scrape.do:8080"
    expected_proxy_mode_url = f"http://{token}:@{expected_proxy_scrape_do_url}"
    expected_proxies = {
        "http": expected_proxy_mode_url,
        "https": expected_proxy_mode_url,
    }

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = expected_response
        mock_get.return_value = mock_response

        result = scrape_do_fetch(token, target_url, use_proxy=True)

        # For proxy usage without geoCode, params should be an empty dict.
        mock_get.assert_called_once_with(
            target_url, proxies=expected_proxies, verify=False, params={}
        )
        assert result == expected_response


def test_scrape_do_fetch_with_proxy_with_geo():
    """
    Test scrape_do_fetch function using proxy mode with geoCode and super_proxy enabled.
    This test verifies that:
        - The function constructs the correct proxy URL using the default proxy endpoint.
        - The function appends the correct params including geoCode and super proxy flags.
        - The function returns the expected response text.
    """
    token = "test_token"
    target_url = "https://example.net"
    geo_code = "US"
    super_proxy = True
    expected_response = "Mocked proxy response US"

    expected_proxy_scrape_do_url = "proxy.scrape.do:8080"
    expected_proxy_mode_url = f"http://{token}:@{expected_proxy_scrape_do_url}"
    expected_proxies = {
        "http": expected_proxy_mode_url,
        "https": expected_proxy_mode_url,
    }

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = expected_response
        mock_get.return_value = mock_response

        result = scrape_do_fetch(
            token, target_url, use_proxy=True, geoCode=geo_code, super_proxy=super_proxy
        )

        expected_params = {"geoCode": geo_code, "super": "true"}
        mock_get.assert_called_once_with(
            target_url, proxies=expected_proxies, verify=False, params=expected_params
        )
        assert result == expected_response


def test_scrape_do_fetch_without_proxy_custom_env():
    """
    Test scrape_do_fetch using API mode with a custom API_SCRAPE_DO_URL environment variable.
    """
    token = "custom_token"
    target_url = "https://custom-example.com"
    encoded_url = urllib.parse.quote(target_url)
    expected_response = "Custom API response"

    with patch.dict("os.environ", {"API_SCRAPE_DO_URL": "custom.api.scrape.do"}):
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = expected_response
            mock_get.return_value = mock_response

            result = scrape_do_fetch(token, target_url, use_proxy=False)

            expected_url = (
                f"http://custom.api.scrape.do?token={token}&url={encoded_url}"
            )
            mock_get.assert_called_once_with(expected_url)
            assert result == expected_response


def test_scrape_do_fetch_with_proxy_custom_env():
    """
    Test scrape_do_fetch using proxy mode with a custom PROXY_SCRAPE_DO_URL environment variable.
    """
    token = "custom_token"
    target_url = "https://custom-example.org"
    expected_response = "Custom proxy response"

    with patch.dict(
        "os.environ", {"PROXY_SCRAPE_DO_URL": "custom.proxy.scrape.do:8888"}
    ):
        expected_proxy_mode_url = f"http://{token}:@custom.proxy.scrape.do:8888"
        expected_proxies = {
            "http": expected_proxy_mode_url,
            "https": expected_proxy_mode_url,
        }

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.text = expected_response
            mock_get.return_value = mock_response

            result = scrape_do_fetch(token, target_url, use_proxy=True)

            mock_get.assert_called_once_with(
                target_url, proxies=expected_proxies, verify=False, params={}
            )
            assert result == expected_response


def test_scrape_do_fetch_exception_propagation():
    """
    Test that scrape_do_fetch properly propagates exceptions raised by requests.get.
    """
    token = "test_token"
    target_url = "https://example.com"

    with patch("requests.get", side_effect=Exception("Network Error")):
        with pytest.raises(Exception) as excinfo:
            scrape_do_fetch(token, target_url, use_proxy=False)
        assert "Network Error" in str(excinfo.value)


def test_scrape_do_fetch_with_proxy_with_geo_and_super_false():
    """
    Test scrape_do_fetch function using proxy mode with geoCode provided and super_proxy set to False.
    This test verifies that the correct proxy URL and parameters (with "super" set to "false") are used.
    """
    token = "test_token"
    target_url = "https://example.co"
    geo_code = "UK"
    super_proxy = False
    expected_response = "Mocked proxy response UK no super"

    expected_proxy_scrape_do_url = "proxy.scrape.do:8080"
    expected_proxy_mode_url = f"http://{token}:@{expected_proxy_scrape_do_url}"
    expected_proxies = {
        "http": expected_proxy_mode_url,
        "https": expected_proxy_mode_url,
    }
    expected_params = {"geoCode": geo_code, "super": "false"}

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = expected_response
        mock_get.return_value = mock_response

        result = scrape_do_fetch(
            token, target_url, use_proxy=True, geoCode=geo_code, super_proxy=super_proxy
        )

        mock_get.assert_called_once_with(
            target_url, proxies=expected_proxies, verify=False, params=expected_params
        )
        assert result == expected_response


def test_scrape_do_fetch_empty_token_without_proxy():
    """
    Test scrape_do_fetch in API mode with an empty token.
    This verifies that even when the token is an empty string, the URL is constructed as expected.
    """
    token = ""
    target_url = "https://emptytoken.com"
    encoded_url = urllib.parse.quote(target_url)
    expected_response = "Empty token response"

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = expected_response
        mock_get.return_value = mock_response

        result = scrape_do_fetch(token, target_url, use_proxy=False)

        expected_url = f"http://api.scrape.do?token={token}&url={encoded_url}"
        mock_get.assert_called_once_with(expected_url)
        assert result == expected_response


def test_scrape_do_fetch_with_proxy_with_empty_geo():
    """
    Test scrape_do_fetch function using proxy mode with an empty geoCode string.
    Even though geoCode is provided (as an empty string), it should be treated as false
    and not result in params being set.
    """
    token = "test_token"
    target_url = "https://example.empty"
    geo_code = ""
    super_proxy = True
    expected_response = "Mocked proxy response empty geo"

    expected_proxy_scrape_do_url = "proxy.scrape.do:8080"
    expected_proxy_mode_url = f"http://{token}:@{expected_proxy_scrape_do_url}"
    expected_proxies = {
        "http": expected_proxy_mode_url,
        "https": expected_proxy_mode_url,
    }
    # Since geo_code is an empty string, the condition will be false and params should be an empty dict.

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = expected_response
        mock_get.return_value = mock_response

        result = scrape_do_fetch(
            token, target_url, use_proxy=True, geoCode=geo_code, super_proxy=super_proxy
        )

        mock_get.assert_called_once_with(
            target_url, proxies=expected_proxies, verify=False, params={}
        )
        assert result == expected_response


def test_scrape_do_fetch_api_encoding_special_characters():
    """
    Test scrape_do_fetch function in API mode with a target URL that includes query parameters
    and special characters. This test verifies that the URL gets properly URL-encoded.
    """
    token = "special_token"
    # target_url includes query parameters and characters that need URL encoding
    target_url = "https://example.com/path?param=value&other=1"
    encoded_url = urllib.parse.quote(target_url)
    expected_response = "Encoded API response"

    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.text = expected_response
        mock_get.return_value = mock_response

        result = scrape_do_fetch(token, target_url, use_proxy=False)

        expected_url = f"http://api.scrape.do?token={token}&url={encoded_url}"
        mock_get.assert_called_once_with(expected_url)
        assert result == expected_response
