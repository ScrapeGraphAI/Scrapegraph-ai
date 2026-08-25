"""Load public X posts through the Xquik API."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Sequence
from typing import Any, Protocol, cast

from langchain_community.document_loaders.base import BaseLoader
from langchain_core.documents import Document

_TWEET_ID = re.compile(r"^\d{1,20}$")
_TWEET_URL = re.compile(
    r"^https?://(?:(?:www|mobile)\.)?(?:x|twitter)\.com/[^/]+/status/"
    r"(\d{1,20})(?:[/?#].*)?$",
    re.IGNORECASE,
)


class _TweetResponse(Protocol):
    def model_dump(self, *, by_alias: bool, exclude_none: bool) -> dict[str, Any]: ...


class _TweetsResource(Protocol):
    def retrieve(self, tweet_id: str) -> _TweetResponse: ...


class _XResource(Protocol):
    @property
    def tweets(self) -> _TweetsResource: ...


class _XquikClient(Protocol):
    @property
    def x(self) -> _XResource: ...

    def close(self) -> None: ...


def extract_tweet_id(source: str) -> str:
    """Return the tweet ID from a numeric ID or public X status URL."""
    value = source.strip()
    if _TWEET_ID.fullmatch(value):
        return value

    match = _TWEET_URL.fullmatch(value)
    if match:
        return match.group(1)

    raise ValueError(
        "XquikLoader requires a numeric tweet ID or an x.com/twitter.com status URL."
    )


def _create_client(api_key: str | None, timeout: float) -> _XquikClient:
    try:
        from x_twitter_scraper import XTwitterScraper
    except ImportError as exc:
        raise ImportError(
            "XquikLoader requires x_twitter_scraper. "
            "Install it with `pip install x_twitter_scraper`."
        ) from exc

    return cast(
        _XquikClient,
        XTwitterScraper(api_key=api_key, timeout=timeout),
    )


class XquikLoader(BaseLoader):
    """Fetch public X posts as LangChain documents.

    Each source must be a numeric tweet ID or a public ``x.com`` or
    ``twitter.com`` status URL. The loader uses the published Xquik tweet lookup
    API and stores the complete response as JSON for downstream extraction.

    Args:
        sources: Tweet IDs or public status URLs.
        api_key: Xquik API key. The SDK reads ``X_TWITTER_SCRAPER_API_KEY`` when
            omitted.
        timeout: Request timeout in seconds.
        client: Optional configured Xquik client.
    """

    def __init__(
        self,
        sources: Sequence[str],
        *,
        api_key: str | None = None,
        timeout: float = 30.0,
        client: _XquikClient | None = None,
    ) -> None:
        self.sources = list(sources)
        self.api_key = api_key
        self.timeout = timeout
        self._client = client

    def lazy_load(self) -> Iterator[Document]:
        """Yield one document for each X post."""
        owns_client = self._client is None
        client = self._client or _create_client(self.api_key, self.timeout)

        try:
            for source in self.sources:
                tweet_id = extract_tweet_id(source)
                response = client.x.tweets.retrieve(tweet_id)
                payload = response.model_dump(by_alias=True, exclude_none=True)
                yield Document(
                    page_content=json.dumps(
                        payload,
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    metadata={
                        "source": source,
                        "loader": "xquik",
                        "tweet_id": tweet_id,
                    },
                )
        finally:
            if owns_client:
                client.close()
