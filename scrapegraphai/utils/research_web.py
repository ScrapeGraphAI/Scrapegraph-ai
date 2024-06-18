"""
Module for making the request on the web
"""
import re
from typing import List
from langchain_community.tools import DuckDuckGoSearchResults
from googlesearch import search as google_search


def search_on_web(query: str, search_engine: str = "Google", max_results: int = 10) -> List[str]:
    """
    Searches the web for a given query using specified search engine options.

    Args:
        query (str): The search query to find on the internet.
        search_engine (str, optional): Specifies the search engine to use, options include 'Google' or 'DuckDuckGo'. Default is 'Google'.
        max_results (int, optional): The maximum number of search results to return.

    Returns:
        List[str]: A list of URLs as strings that are the search results.

    Raises:
        ValueError: If the search engine specified is neither 'Google' nor 'DuckDuckGo'.

    Example:
        >>> search_on_web("example query", search_engine="Google", max_results=5)
        ['http://example.com', 'http://example.org', ...]

    This function allows switching between Google and DuckDuckGo to perform 
    internet searches, returning a list of result URLs.
    """

    if search_engine.lower() == "google":
        res = []

        for url in google_search(query, stop=max_results):
            res.append(url)
        return res
    elif search_engine.lower() == "duckduckgo":
        research = DuckDuckGoSearchResults(max_results=max_results)
        res = research.run(query)

        links = re.findall(r'https?://[^\s,\]]+', res)

        return links
    raise ValueError(
        "The only search engines available are DuckDuckGo or Google")
