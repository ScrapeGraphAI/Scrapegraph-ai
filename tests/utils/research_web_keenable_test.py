"""Mock-based tests for the Keenable engine in search_on_web (no network)."""

from unittest.mock import MagicMock, patch

import pytest

from scrapegraphai.utils.research_web import (
    KEENABLE_API_URL,
    KEENABLE_PUBLIC_API_URL,
    SearchRequestError,
    search_on_web,
)

# search_on_web is rate limited (10 calls/minute), so call the undecorated function.
search = search_on_web.__wrapped__

RESPONSE = {
    "query": "q",
    "mode": "pro",
    "results": [
        {"title": "A", "url": "https://a.example/", "snippet": "a"},
        {"title": "Doc", "url": "https://b.example/report.pdf", "snippet": "pdf"},
        {"title": "C", "url": "https://c.example/", "snippet": "c"},
        {"title": "No URL", "snippet": "skipped"},
    ],
}


def _response(payload=RESPONSE):
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


@pytest.fixture(autouse=True)
def _no_env_key(monkeypatch):
    monkeypatch.delenv("KEENABLE_API_KEY", raising=False)


def test_keyless_uses_public_endpoint_with_app_title():
    with patch(
        "scrapegraphai.utils.research_web.requests.post", return_value=_response()
    ) as post:
        results = search("q", search_engine="keenable", max_results=5)

    assert results == ["https://a.example/", "https://c.example/"]
    args, kwargs = post.call_args
    assert args[0] == KEENABLE_PUBLIC_API_URL
    assert kwargs["headers"]["X-Keenable-Title"] == "scrapegraphai"
    assert "X-API-Key" not in kwargs["headers"]
    assert kwargs["json"] == {"query": "q", "max_results": 5}


def test_api_key_uses_authenticated_endpoint():
    with patch(
        "scrapegraphai.utils.research_web.requests.post", return_value=_response()
    ) as post:
        search("q", search_engine="Keenable", keenable_api_key="keen_test")

    args, kwargs = post.call_args
    assert args[0] == KEENABLE_API_URL
    assert kwargs["headers"]["X-API-Key"] == "keen_test"


def test_api_key_from_environment(monkeypatch):
    monkeypatch.setenv("KEENABLE_API_KEY", "keen_env")
    with patch(
        "scrapegraphai.utils.research_web.requests.post", return_value=_response()
    ) as post:
        search("q", search_engine="keenable")

    args, kwargs = post.call_args
    assert args[0] == KEENABLE_API_URL
    assert kwargs["headers"]["X-API-Key"] == "keen_env"


def test_max_results_is_capped_at_keenables_limit():
    with patch(
        "scrapegraphai.utils.research_web.requests.post", return_value=_response()
    ) as post:
        search("q", search_engine="keenable", max_results=100)

    assert post.call_args.kwargs["json"]["max_results"] == 50


def test_results_are_trimmed_to_max_results():
    with patch(
        "scrapegraphai.utils.research_web.requests.post", return_value=_response()
    ):
        results = search("q", search_engine="keenable", max_results=1)

    assert results == ["https://a.example/"]


def test_http_error_is_a_search_request_error():
    response = _response()
    response.raise_for_status.side_effect = Exception("429 Too Many Requests")
    with patch("scrapegraphai.utils.research_web.requests.post", return_value=response):
        with pytest.raises(SearchRequestError, match="Keenable search failed"):
            search("q", search_engine="keenable")
