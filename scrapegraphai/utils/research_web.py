"""
research_web module
"""

import re
from typing import List

import requests
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchResults


def search_on_web(
    query: str,
    search_engine: str = "duckduckgo",
    max_results: int = 10,
    port: int = 8080,
    timeout: int = 10,
    proxy: str | dict = None,
    serper_api_key: str = None,
    region: str = None,
    language: str = "en",
) -> List[str]:
    """Search web function with improved error handling and validation

    Args:
        query (str): Search query
        search_engine (str): Search engine to use
        max_results (int): Maximum number of results to return
        port (int): Port for SearXNG
        timeout (int): Request timeout in seconds
        proxy (str | dict): Proxy configuration
        serper_api_key (str): API key for Serper
        region (str): Country/region code (e.g., 'mx' for Mexico)
        language (str): Language code (e.g., 'es' for Spanish)
    """

    # Input validation
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")

    search_engine = search_engine.lower()
    valid_engines = {"duckduckgo", "bing", "searxng", "serper"}
    if search_engine not in valid_engines:
        raise ValueError(f"Search engine must be one of: {', '.join(valid_engines)}")

    # Format proxy once
    formatted_proxy = None
    if proxy:
        formatted_proxy = format_proxy(proxy)

    try:
        results = []
        if search_engine == "duckduckgo":
            # Create a DuckDuckGo search object with max_results
            research = DuckDuckGoSearchResults(max_results=max_results)
            # Run the search
            res = research.run(query)
            # Extract URLs using regex
            results = re.findall(r"https?://[^\s,\]]+", res)

        elif search_engine == "bing":
            results = _search_bing(query, max_results, timeout, formatted_proxy)

        elif search_engine == "searxng":
            results = _search_searxng(query, max_results, port, timeout)

        elif search_engine == "serper":
            results = _search_serper(query, max_results, serper_api_key, timeout)

        return filter_pdf_links(results)

    except requests.Timeout:
        raise TimeoutError(f"Search request timed out after {timeout} seconds")
    except requests.RequestException as e:
        raise RuntimeError(f"Search request failed: {str(e)}")


def _search_bing(
    query: str, max_results: int, timeout: int, proxy: str = None
) -> List[str]:
    """Helper function for Bing search"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    search_url = f"https://www.bing.com/search?q={query}"

    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = requests.get(
        search_url, headers=headers, timeout=timeout, proxies=proxies
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    return [
        result.find("a")["href"]
        for result in soup.find_all("li", class_="b_algo", limit=max_results)
    ]


def _search_searxng(query: str, max_results: int, port: int, timeout: int) -> List[str]:
    """Helper function for SearXNG search"""
    url = f"http://localhost:{port}/search"
    params = {
        "q": query,
        "format": "json",
        "engines": "google,duckduckgo,brave,qwant,bing",
    }
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return [
        result["url"] for result in response.json().get("results", [])[:max_results]
    ]


def _search_serper(
    query: str, max_results: int, serper_api_key: str, timeout: int
) -> List[str]:
    """Helper function for Serper API to get Google search results"""
    if not serper_api_key:
        raise ValueError("API key is required for Serper API")

    url = "https://google.serper.dev/search"
    payload = {"q": query, "num": max_results}

    headers = {"X-API-KEY": serper_api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,  # requests will handle JSON serialization
            timeout=timeout,
        )
        response.raise_for_status()

        # Extract only the organic search results
        results = response.json()
        organic_results = results.get("organic", [])
        urls = [result.get("link") for result in organic_results if result.get("link")]

        return urls[:max_results]

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Serper API request failed: {str(e)}")


def format_proxy(proxy):
    if isinstance(proxy, dict):
        server = proxy.get("server")
        username = proxy.get("username")
        password = proxy.get("password")

        if all([username, password, server]):
            proxy_url = f"http://{username}:{password}@{server}"
            return proxy_url
        else:
            raise ValueError("Proxy dictionary is missing required fields.")
    elif isinstance(proxy, str):
        return proxy  # "https://username:password@ip:port"
    else:
        raise TypeError("Proxy should be a dictionary or a string.")


def filter_pdf_links(links: List[str]) -> List[str]:
    """
    Filters out any links that point to PDF files.

    Args:
        links (List[str]): A list of URLs as strings.

    Returns:
        List[str]: A list of URLs excluding any that end with '.pdf'.
    """
    return [link for link in links if not link.lower().endswith(".pdf")]
