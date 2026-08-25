"""Tests for the Xquik document loader."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from scrapegraphai.docloaders.xquik import XquikLoader, extract_tweet_id
from scrapegraphai.graphs.smart_scraper_graph import SmartScraperGraph


class _Response:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    def model_dump(self, *, by_alias: bool, exclude_none: bool) -> dict[str, Any]:
        assert by_alias is True
        assert exclude_none is True
        return self.payload


class _Tweets:
    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def retrieve(self, tweet_id: str) -> _Response:
        self.calls.append(tweet_id)
        return _Response(self.responses[tweet_id])


class _X:
    def __init__(self, tweets: _Tweets) -> None:
        self.tweets = tweets


class _Client:
    def __init__(self, responses: dict[str, dict[str, Any]]) -> None:
        self.tweets = _Tweets(responses)
        self.x = _X(self.tweets)
        self.closed = False

    def close(self) -> None:
        self.closed = True


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("1893456789012345678", "1893456789012345678"),
        (
            "https://x.com/example/status/1893456789012345678",
            "1893456789012345678",
        ),
        (
            "https://mobile.twitter.com/example/status/1893456789012345678?s=20",
            "1893456789012345678",
        ),
    ],
)
def test_extract_tweet_id(source: str, expected: str) -> None:
    assert extract_tweet_id(source) == expected


@pytest.mark.parametrize(
    "source",
    [
        "https://example.com/status/1893456789012345678",
        "https://x.com/example",
        "not-a-tweet",
    ],
)
def test_extract_tweet_id_rejects_invalid_sources(source: str) -> None:
    with pytest.raises(ValueError, match="numeric tweet ID"):
        extract_tweet_id(source)


def test_loader_returns_complete_tweet_json_and_metadata() -> None:
    tweet_id = "1893456789012345678"
    payload = {
        "tweet": {
            "id": tweet_id,
            "text": "Scrape structured data from this post.",
            "likeCount": 12,
        },
        "author": {"username": "example"},
    }
    client = _Client({tweet_id: payload})

    documents = XquikLoader(
        [f"https://x.com/example/status/{tweet_id}"],
        client=client,
    ).load()

    assert len(documents) == 1
    assert json.loads(documents[0].page_content) == payload
    assert documents[0].metadata == {
        "source": f"https://x.com/example/status/{tweet_id}",
        "loader": "xquik",
        "tweet_id": tweet_id,
    }
    assert client.tweets.calls == [tweet_id]
    assert client.closed is False


def test_loader_fetches_each_source_in_order() -> None:
    first = "1893456789012345678"
    second = "1893456789012345679"
    client = _Client(
        {
            first: {"tweet": {"id": first, "text": "First"}},
            second: {"tweet": {"id": second, "text": "Second"}},
        }
    )

    documents = XquikLoader([first, second], client=client).load()

    assert [document.metadata["tweet_id"] for document in documents] == [
        first,
        second,
    ]
    assert client.tweets.calls == [first, second]


def test_loader_closes_its_client(monkeypatch: pytest.MonkeyPatch) -> None:
    tweet_id = "1893456789012345678"
    client = _Client({tweet_id: {"tweet": {"id": tweet_id, "text": "Post"}}})
    monkeypatch.setattr(
        "scrapegraphai.docloaders.xquik._create_client",
        lambda api_key, timeout: client,
    )

    documents = XquikLoader([tweet_id]).load()

    assert len(documents) == 1
    assert client.closed is True


def test_smart_scraper_passes_fetch_backend_configuration() -> None:
    graph = object.__new__(SmartScraperGraph)
    graph.llm_model = object()
    graph.config = {
        "xquik": {"api_key": "test-key"},
    }
    graph.prompt = "Extract the post text."
    graph.source = "https://x.com/example/status/1893456789012345678"
    graph.schema = None
    graph.model_token = 8192

    with (
        patch("scrapegraphai.graphs.smart_scraper_graph.FetchNode") as fetch_node,
        patch("scrapegraphai.graphs.smart_scraper_graph.ParseNode"),
        patch("scrapegraphai.graphs.smart_scraper_graph.GenerateAnswerNode"),
        patch(
            "scrapegraphai.graphs.smart_scraper_graph.BaseGraph",
            return_value=MagicMock(),
        ),
    ):
        graph._create_graph()

    node_config = fetch_node.call_args.kwargs["node_config"]
    assert node_config["xquik"] == {"api_key": "test-key"}


def test_smart_scraper_treats_numeric_tweet_id_as_url_input() -> None:
    with patch(
        "scrapegraphai.graphs.smart_scraper_graph.AbstractGraph.__init__",
        return_value=None,
    ):
        graph = SmartScraperGraph(
            prompt="Extract the post text.",
            source="1893456789012345678",
            config={"xquik": {"api_key": "test-key"}},
        )

    assert graph.input_key == "url"
