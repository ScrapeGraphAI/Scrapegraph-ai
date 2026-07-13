import pytest
from unittest.mock import MagicMock, patch

from scrapegraphai.utils.research_web import (
    SearchRequestError,
    _run_with_retries,
    get_random_user_agent,
    search_on_web,
)


def test_run_with_retries_succeeds_after_failures():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise SearchRequestError("transient")
        return "ok"

    assert _run_with_retries(flaky, max_retries=2) == "ok"
    assert calls["n"] == 3


def test_run_with_retries_exhausted_raises():
    calls = {"n": 0}

    def always_fail():
        calls["n"] += 1
        raise SearchRequestError("boom")

    with pytest.raises(SearchRequestError):
        _run_with_retries(always_fail, max_retries=2)
    assert calls["n"] == 3


def test_run_with_retries_zero_retries_no_retry():
    calls = {"n": 0}

    def always_fail():
        calls["n"] += 1
        raise SearchRequestError("boom")

    with pytest.raises(SearchRequestError):
        _run_with_retries(always_fail, max_retries=0)
    assert calls["n"] == 1


@patch("scrapegraphai.utils.research_web.requests.get")
def test_search_on_web_retries_then_succeeds(mock_get):
    resp = MagicMock()
    resp.status_code = 200
    resp.text = "<html></html>"
    resp.raise_for_status = MagicMock()
    # First attempt is blocked (raises), second succeeds
    mock_get.side_effect = [Exception("403 blocked"), resp]
    result = search_on_web("query", search_engine="bing", max_results=1, max_retries=1)
    assert result == []
    assert mock_get.call_count == 2


@patch("scrapegraphai.utils.research_web.requests.get")
def test_search_on_web_retries_exhausted(mock_get):
    mock_get.side_effect = Exception("403 blocked")
    with pytest.raises(SearchRequestError):
        search_on_web("query", search_engine="bing", max_results=1, max_retries=2)
    assert mock_get.call_count == 3


@patch("scrapegraphai.utils.research_web.requests.get")
@patch("scrapegraphai.utils.research_web.get_random_user_agent")
def test_search_bing_uses_random_user_agent(mock_ua, mock_get):
    mock_ua.return_value = "UA-TEST"
    resp = MagicMock()
    resp.status_code = 200
    resp.text = "<html></html>"
    resp.raise_for_status = MagicMock()
    mock_get.return_value = resp

    results = search_on_web("query", search_engine="bing", max_results=1, max_retries=0)
    assert results == []
    mock_ua.assert_called()
    _, kwargs = mock_get.call_args
    assert kwargs["headers"]["User-Agent"] == "UA-TEST"


@patch("scrapegraphai.utils.research_web.requests.get")
@patch("scrapegraphai.utils.research_web.get_random_user_agent")
def test_search_bing_rotates_ua_on_retry(mock_ua, mock_get):
    mock_ua.side_effect = ["UA-1", "UA-2"]
    resp = MagicMock()
    resp.status_code = 200
    resp.text = "<html></html>"
    resp.raise_for_status = MagicMock()
    # First attempt is blocked (raises), second succeeds
    mock_get.side_effect = [Exception("403 blocked"), resp]

    search_on_web("query", search_engine="bing", max_results=1, max_retries=1)

    assert mock_ua.call_count == 2
    assert mock_get.call_count == 2
