"""
research_web module for web searching across different search engines with improved
error handling, validation, and security features.
"""

import random
import re
import time
from functools import wraps
from typing import Dict, List, Optional, Union

import requests
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchResults
from pydantic import BaseModel, Field, validator


class ResearchWebError(Exception):
    """Base exception for research web errors."""

    pass


class SearchConfigError(ResearchWebError):
    """Exception raised when search configuration is invalid."""

    pass


class SearchRequestError(ResearchWebError):
    """Exception raised when search request fails."""

    pass


class ProxyConfig(BaseModel):
    """Model for proxy configuration validation."""

    server: str = Field(..., description="Proxy server address including port")
    username: Optional[str] = Field(
        None, description="Username for proxy authentication"
    )
    password: Optional[str] = Field(
        None, description="Password for proxy authentication"
    )


class SearchConfig(BaseModel):
    """Model for search configuration validation."""

    query: str = Field(..., description="Search query")
    search_engine: str = Field("duckduckgo", description="Search engine to use")
    max_results: int = Field(10, description="Maximum number of results to return")
    port: Optional[int] = Field(8080, description="Port for SearXNG")
    timeout: int = Field(10, description="Request timeout in seconds")
    proxy: Optional[Union[str, Dict, ProxyConfig]] = Field(
        None, description="Proxy configuration"
    )
    serper_api_key: Optional[str] = Field(None, description="API key for Serper")
    region: Optional[str] = Field(None, description="Country/region code")
    language: str = Field("en", description="Language code")

    @validator("search_engine")
    def validate_search_engine(cls, v):
        """Validate search engine."""
        valid_engines = {"duckduckgo", "bing", "searxng", "serper"}
        if v.lower() not in valid_engines:
            raise ValueError(
                f"Search engine must be one of: {', '.join(valid_engines)}"
            )
        return v.lower()

    @validator("query")
    def validate_query(cls, v):
        """Validate search query."""
        if not v or not isinstance(v, str):
            raise ValueError("Query must be a non-empty string")
        return v

    @validator("max_results")
    def validate_max_results(cls, v):
        """Validate max results."""
        if v < 1 or v > 100:
            raise ValueError("max_results must be between 1 and 100")
        return v


# Define advanced PDF detection regex
PDF_REGEX = re.compile(r"\.pdf(#.*)?(\?.*)?$", re.IGNORECASE)


# Rate limiting decorator
def rate_limited(calls: int, period: int = 60):
    """
    Decorator to limit the rate of function calls.

    Args:
        calls (int): Maximum number of calls allowed in the period.
        period (int): Time period in seconds.

    Returns:
        Callable: Decorated function with rate limiting.
    """
    min_interval = period / float(calls)
    last_called = [0.0]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result

        return wrapper

    return decorator


def sanitize_search_query(query: str) -> str:
    """
    Sanitizes search query to prevent injection attacks.

    Args:
        query (str): The search query.

    Returns:
        str: Sanitized query.
    """
    # Remove potential command injection characters
    sanitized = re.sub(r"[;&|`$()\[\]{}<>]", "", query)
    # Trim whitespace
    sanitized = sanitized.strip()
    return sanitized


# List of user agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
]


def get_random_user_agent() -> str:
    """
    Returns a random user agent from the list.

    Returns:
        str: Random user agent string.
    """
    return random.choice(USER_AGENTS)


@rate_limited(calls=10, period=60)
def search_on_web(
    query: str,
    search_engine: str = "duckduckgo",
    max_results: int = 10,
    port: int = 8080,
    timeout: int = 10,
    proxy: Optional[Union[str, Dict, ProxyConfig]] = None,
    serper_api_key: Optional[str] = None,
    region: Optional[str] = None,
    language: str = "en",
) -> List[str]:
    """
    Search web function with improved error handling, validation, and security features.

    Args:
        query (str): Search query
        search_engine (str): Search engine to use
        max_results (int): Maximum number of results to return
        port (int): Port for SearXNG
        timeout (int): Request timeout in seconds
        proxy (str | dict | ProxyConfig): Proxy configuration
        serper_api_key (str): API key for Serper
        region (str): Country/region code (e.g., 'mx' for Mexico)
        language (str): Language code (e.g., 'es' for Spanish)

    Returns:
        List[str]: List of URLs from search results

    Raises:
        SearchConfigError: If search configuration is invalid
        SearchRequestError: If search request fails
        TimeoutError: If search request times out
    """
    try:
        # Sanitize query for security
        sanitized_query = sanitize_search_query(query)

        # Validate search configuration
        config = SearchConfig(
            query=sanitized_query,
            search_engine=search_engine,
            max_results=max_results,
            port=port,
            timeout=timeout,
            proxy=proxy,
            serper_api_key=serper_api_key,
            region=region,
            language=language,
        )

        # Format proxy once
        formatted_proxy = None
        if config.proxy:
            formatted_proxy = format_proxy(config.proxy)

        results = []
        if config.search_engine == "duckduckgo":
            # Create a DuckDuckGo search object with max_results
            research = DuckDuckGoSearchResults(max_results=config.max_results)
            # Run the search
            res = research.run(config.query)
            # Extract URLs using regex
            results = re.findall(r"https?://[^\s,\]]+", res)

        elif config.search_engine == "bing":
            results = _search_bing(
                config.query, config.max_results, config.timeout, formatted_proxy
            )

        elif config.search_engine == "searxng":
            results = _search_searxng(
                config.query, config.max_results, config.port, config.timeout
            )

        elif config.search_engine == "serper":
            results = _search_serper(
                config.query, config.max_results, config.serper_api_key, config.timeout
            )

        return filter_pdf_links(results)

    except requests.Timeout:
        raise TimeoutError(f"Search request timed out after {timeout} seconds")
    except requests.RequestException as e:
        raise SearchRequestError(f"Search request failed: {str(e)}")
    except ValueError as e:
        raise SearchConfigError(f"Invalid search configuration: {str(e)}")


def _search_bing(
    query: str, max_results: int, timeout: int, proxy: Optional[str] = None
) -> List[str]:
    """
    Helper function for Bing search with improved error handling.

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        timeout (int): Request timeout in seconds
        proxy (str, optional): Proxy configuration

    Returns:
        List[str]: List of URLs from search results
    """
    headers = {"User-Agent": get_random_user_agent()}

    params = {"q": query, "count": max_results}

    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        response = requests.get(
            "https://www.bing.com/search",
            params=params,
            headers=headers,
            proxies=proxies,
            timeout=timeout,
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # Extract URLs from Bing search results
        for link in soup.select("li.b_algo h2 a"):
            url = link.get("href")
            if url and url.startswith("http"):
                results.append(url)
                if len(results) >= max_results:
                    break

        return results
    except Exception as e:
        raise SearchRequestError(f"Bing search failed: {str(e)}")


def _search_searxng(query: str, max_results: int, port: int, timeout: int) -> List[str]:
    """
    Helper function for SearXNG search.

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        port (int): Port for SearXNG
        timeout (int): Request timeout in seconds

    Returns:
        List[str]: List of URLs from search results
    """
    headers = {"User-Agent": get_random_user_agent()}

    params = {
        "q": query,
        "format": "json",
        "categories": "general",
        "language": "en",
        "time_range": "",
        "engines": "duckduckgo,bing,brave",
        "results": max_results,
    }

    try:
        response = requests.get(
            f"http://localhost:{port}/search",
            params=params,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()

        json_data = response.json()
        results = [result["url"] for result in json_data.get("results", [])]
        return results[:max_results]
    except Exception as e:
        raise SearchRequestError(f"SearXNG search failed: {str(e)}")


def _search_serper(
    query: str, max_results: int, api_key: str, timeout: int
) -> List[str]:
    """
    Helper function for Serper search.

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        api_key (str): API key for Serper
        timeout (int): Request timeout in seconds

    Returns:
        List[str]: List of URLs from search results
    """
    if not api_key:
        raise SearchConfigError("Serper API key is required")

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}

    data = {"q": query, "num": max_results}

    try:
        response = requests.post(
            "https://google.serper.dev/search",
            json=data,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()

        json_data = response.json()
        results = []

        # Extract organic search results
        for item in json_data.get("organic", []):
            if "link" in item:
                results.append(item["link"])
                if len(results) >= max_results:
                    break

        return results
    except Exception as e:
        raise SearchRequestError(f"Serper search failed: {str(e)}")


def format_proxy(proxy_config: Union[str, Dict, ProxyConfig]) -> str:
    """
    Format proxy configuration into a string.

    Args:
        proxy_config: Proxy configuration as string, dict, or ProxyConfig

    Returns:
        str: Formatted proxy string
    """
    if isinstance(proxy_config, str):
        return proxy_config

    if isinstance(proxy_config, dict):
        proxy_config = ProxyConfig(**proxy_config)

    # Format proxy with authentication if provided
    if proxy_config.username and proxy_config.password:
        auth = f"{proxy_config.username}:{proxy_config.password}@"
        return f"http://{auth}{proxy_config.server}"

    return f"http://{proxy_config.server}"


def filter_pdf_links(urls: List[str]) -> List[str]:
    """
    Filter out PDF links from search results.

    Args:
        urls (List[str]): List of URLs

    Returns:
        List[str]: Filtered list of URLs without PDFs
    """
    return [url for url in urls if not PDF_REGEX.search(url)]


def verify_request_signature(
    request_data: Dict, signature: str, secret_key: str
) -> bool:
    """
    Verify the signature of an incoming request.

    Args:
        request_data (Dict): Request data to verify
        signature (str): Provided signature
        secret_key (str): Secret key for verification

    Returns:
        bool: True if signature is valid, False otherwise
    """
    import hashlib
    import hmac
    import json

    # Sort keys for consistent serialization
    data_string = json.dumps(request_data, sort_keys=True)

    # Create HMAC signature
    computed_signature = hmac.new(
        secret_key.encode(), data_string.encode(), hashlib.sha256
    ).hexdigest()

    # Compare signatures using constant-time comparison to prevent timing attacks
    return hmac.compare_digest(computed_signature, signature)
