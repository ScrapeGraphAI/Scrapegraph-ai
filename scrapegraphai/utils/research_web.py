""" 
Module for making the request on the web
"""
import re
from typing import List
from langchain_community.tools import DuckDuckGoSearchResults
from googlesearch import search


def search_on_web(query: str, search_engine: str = "Google", max_results: int = 10) -> List[str]:
    """ 
    Function that given a query it finds it on the intenet
    Args:
        query (str): query to search on internet
        search_engine (str, optional): type of browser, it could be DuckDuckGo or Google,
            default: Google
        max_results (int, optional): maximum number of results

    Returns:
        List[str]: List of strings of web link
    """

    if search_engine == "Google":
        res = []

        for url in search(query, stop=max_results):
            res.append(url)
        return res
    elif search_engine == "DuckDuckGo":
        research = DuckDuckGoSearchResults(max_results=max_results)
        res = research.run(query)

        links = re.findall(r'https?://[^\s,\]]+', res)

        return links
    raise ValueError(
        "The only search engines avaiable are DuckDuckGo or Google")
