"""
Compatibility layer for the scrapegraph-py SDK (>=2.1.1).

The SDK exposes `ScrapeGraphAI` with ergonomic kwargs (PR #88) and wraps
results in `ApiResult[T]`. This module hides those details from the rest
of the codebase so call sites stay terse.
"""

from __future__ import annotations

from typing import Any, Optional, Type

from pydantic import BaseModel


def _schema_to_dict(schema: Optional[Type[BaseModel]]) -> Optional[dict]:
    if schema is None:
        return None
    if isinstance(schema, dict):
        return schema
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        return schema.model_json_schema()
    return None


def _unwrap_result(result: Any) -> dict:
    if hasattr(result, "status") and hasattr(result, "data"):
        if result.status != "success":
            raise RuntimeError(
                getattr(result, "error", "scrapegraph-py request failed")
            )
        data = result.data
        if hasattr(data, "model_dump"):
            return data.model_dump(by_alias=True, exclude_none=True)
        return data if isinstance(data, dict) else {"data": data}
    return result


def _client(api_key: Optional[str]):
    from scrapegraph_py import ScrapeGraphAI

    return ScrapeGraphAI(api_key=api_key)


def extract(
    api_key: Optional[str],
    url: str,
    prompt: str,
    schema: Optional[Type[BaseModel]] = None,
) -> dict:
    """Call the scrapegraph-py extract endpoint."""
    kwargs: dict[str, Any] = {"url": url}
    schema_dict = _schema_to_dict(schema)
    if schema_dict is not None:
        kwargs["schema"] = schema_dict
    with _client(api_key) as client:
        return _unwrap_result(client.extract(prompt, **kwargs))


def scrape(api_key: Optional[str], url: str) -> dict:
    """Call the scrapegraph-py scrape endpoint."""
    with _client(api_key) as client:
        return _unwrap_result(client.scrape(url))


def search(api_key: Optional[str], query: str) -> dict:
    """Call the scrapegraph-py search endpoint."""
    with _client(api_key) as client:
        return _unwrap_result(client.search(query))
