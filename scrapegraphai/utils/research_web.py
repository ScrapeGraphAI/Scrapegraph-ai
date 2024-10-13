"""
research_web module
"""
import re
from typing import List
from langchain_community.tools import DuckDuckGoSearchResults
from googlesearch import search as google_search
import requests
from bs4 import BeautifulSoup

def search_on_web(query: str, search_engine: str = "Google",
                  max_results: int = 10, port: int = 8080, 
                  timeout: int = 10, proxy: str | dict = None) -> List[str]:
    """
    Searches the web for a given query using specified search
    engine options and filters out PDF links.

    Args:
        query (str): The search query to find on the internet.
        search_engine (str, optional): Specifies the search engine to use, 
        options include 'Google', 'DuckDuckGo', 'Bing', or 'SearXNG'. Default is 'Google'.
        max_results (int, optional): The maximum number of search results to return.
        port (int, optional): The port number to use when searching with 'SearXNG'. Default is 8080.
        timeout (int, optional): The number of seconds to wait 
        for a response from a request. Default is 10 seconds.
        proxy (dict or string, optional): The proxy server to use for the request. Default is None. 

    Returns:
        List[str]: A list of URLs as strings that are the search results, excluding any PDF links.

    Raises:
        ValueError: If the search engine specified is not supported.
        requests.exceptions.Timeout: If the request times out.

    Example:
        >>> search_on_web("example query", search_engine="Google", max_results=5)
        ['http://example.com', 'http://example.org', ...]
    """

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

    if proxy:
        proxy = format_proxy(proxy)

    if search_engine.lower() == "google":
        res = []
        for url in google_search(query, num_results=max_results, proxy=proxy):
            res.append(url)
        return filter_pdf_links(res)

    elif search_engine.lower() == "duckduckgo":
        research = DuckDuckGoSearchResults(max_results=max_results)
        res = research.run(query)
        links = re.findall(r'https?://[^\s,\]]+', res)
        return filter_pdf_links(links)

    elif search_engine.lower() == "bing":
        headers = {
            "User-Agent": """Mozilla/5.0 (Windows NT 10.0; Win64; x64) 
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"""
        }
        search_url = f"https://www.bing.com/search?q={query}"
        response = requests.get(search_url, headers=headers, timeout=timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        search_results = []
        for result in soup.find_all('li', class_='b_algo', limit=max_results):
            link = result.find('a')['href']
            search_results.append(link)
        return filter_pdf_links(search_results)

    elif search_engine.lower() == "searxng":
        url = f"http://localhost:{port}"
        params = {"q": query, "format": "json", "engines": "google,duckduckgo,brave,qwant,bing"}
        response = requests.get(url, params=params, timeout=timeout)
        data = response.json()
        limited_results = [result['url'] for result in data["results"][:max_results]]
        return filter_pdf_links(limited_results)

    else:
        raise ValueError("""The only search engines available are
                         DuckDuckGo, Google, Bing, or SearXNG""")
