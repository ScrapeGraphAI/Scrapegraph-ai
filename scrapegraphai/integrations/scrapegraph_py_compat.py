"""
Compatibility layer for scrapegraph-py SDK.

Supports both the v2 `Client` API (PR #82) and the newer `ScrapeGraphAI`
API (PR #84) which uses Pydantic request models and an ApiResult wrapper.
"""

from __future__ import annotations

from typing import Any, Optional, Type

from pydantic import BaseModel


def _detect_api() -> str:
    try:
        from scrapegraph_py import ScrapeGraphAI  # noqa: F401

        return "v3"
    except ImportError:
        pass
    try:
        from scrapegraph_py import Client  # noqa: F401

        return "v2"
    except ImportError as e:
        raise ImportError(
            "scrapegraph_py is not installed. Install it with 'pip install scrapegraph-py'."
        ) from e


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


def extract(
    api_key: Optional[str],
    url: str,
    prompt: str,
    schema: Optional[Type[BaseModel]] = None,
) -> dict:
    """Call the scrapegraph-py extract endpoint across SDK versions."""
    api = _detect_api()

    if api == "v3":
        from scrapegraph_py import ExtractRequest, ScrapeGraphAI

        kwargs: dict[str, Any] = {"url": url, "prompt": prompt}
        schema_dict = _schema_to_dict(schema)
        if schema_dict is not None:
            kwargs["schema_"] = schema_dict
        with ScrapeGraphAI(api_key=api_key) as client:
            return _unwrap_result(client.extract(ExtractRequest(**kwargs)))

    from scrapegraph_py import Client

    with Client(api_key=api_key) as client:
        return client.extract(url=url, prompt=prompt, output_schema=schema)


def scrape(api_key: Optional[str], url: str) -> dict:
    """Call the scrapegraph-py scrape endpoint across SDK versions."""
    api = _detect_api()

    if api == "v3":
        from scrapegraph_py import ScrapeGraphAI, ScrapeRequest

        with ScrapeGraphAI(api_key=api_key) as client:
            return _unwrap_result(client.scrape(ScrapeRequest(url=url)))

    from scrapegraph_py import Client

    with Client(api_key=api_key) as client:
        return client.scrape(url=url)


def search(api_key: Optional[str], query: str) -> dict:
    """Call the scrapegraph-py search endpoint across SDK versions."""
    api = _detect_api()

    if api == "v3":
        from scrapegraph_py import ScrapeGraphAI, SearchRequest

        with ScrapeGraphAI(api_key=api_key) as client:
            return _unwrap_result(client.search(SearchRequest(query=query)))

    from scrapegraph_py import Client

    with Client(api_key=api_key) as client:
        return client.search(query=query)
