"""
research_web module
"""
import re
from typing import List
from langchain_community.tools import DuckDuckGoSearchResults
from googlesearch import search as google_search
import requests
from bs4 import BeautifulSoup
import json

def search_on_web(query: str, search_engine: str = "Google",
                  max_results: int = 10, port: int = 8080,
                  timeout: int = 10, proxy: str | dict = None,
                  serper_api_key: str = None) -> List[str]:
    """Search web function with improved error handling and validation"""
    
    # Input validation
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
        
    search_engine = search_engine.lower()
    valid_engines = {"google", "duckduckgo", "bing", "searxng", "serper"}
    if search_engine not in valid_engines:
        raise ValueError(f"Search engine must be one of: {', '.join(valid_engines)}")

    # Format proxy once
    formatted_proxy = None
    if proxy:
        formatted_proxy = format_proxy(proxy)
        
    try:
        results = []
        if search_engine == "google":
            results = list(google_search(query, num_results=max_results, proxy=formatted_proxy))
            
        elif search_engine == "duckduckgo":
            research = DuckDuckGoSearchResults(max_results=max_results)
            res = research.run(query)
            results = re.findall(r'https?://[^\s,\]]+', res)
            
        elif search_engine == "bing":
            results = _search_bing(query, max_results, timeout, formatted_proxy)
            
        elif search_engine == "searxng":
            results = _search_searxng(query, max_results, port, timeout)
        
        elif search_engine.lower() == "serper":
            results = _search_serper(query, max_results, serper_api_key, timeout)
                
        return filter_pdf_links(results)
        
    except requests.Timeout:
        raise TimeoutError(f"Search request timed out after {timeout} seconds")
    except requests.RequestException as e:
        raise RuntimeError(f"Search request failed: {str(e)}")

def _search_bing(query: str, max_results: int, timeout: int, proxy: str = None) -> List[str]:
    """Helper function for Bing search"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    search_url = f"https://www.bing.com/search?q={query}"
    
    proxies = {"http": proxy, "https": proxy} if proxy else None
    response = requests.get(search_url, headers=headers, timeout=timeout, proxies=proxies)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    return [result.find('a')['href'] for result in soup.find_all('li', class_='b_algo', limit=max_results)]

def _search_searxng(query: str, max_results: int, port: int, timeout: int) -> List[str]:
    """Helper function for SearXNG search"""
    url = f"http://localhost:{port}"
    params = {
        "q": query,
        "format": "json",
        "engines": "google,duckduckgo,brave,qwant,bing"
    }
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return [result['url'] for result in response.json().get("results", [])[:max_results]]

def _search_serper(query: str, max_results: int, serper_api_key: str, timeout: int) -> List[str]:
    """Helper function for serper api"""
    if not serper_api_key:
        raise ValueError("API key is required for serper api.")
    
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "num": max_results
    })
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload, timeout=timeout)
    response.raise_for_status()
    return [result.get("link") for result in response.json().get("organic", [])]


def format_proxy(proxy):
    if isinstance(proxy, dict):
        server = proxy.get('server')
        username = proxy.get('username')
        password = proxy.get('password')

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
    return [link for link in links if not link.lower().endswith('.pdf')]