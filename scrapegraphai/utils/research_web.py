""" 
Module for making the request on the web
"""
import re
from typing import List
from langchain_community.tools import DuckDuckGoSearchResults
from googlesearch import search


def search_on_web(query: str, web_browser: str = "Google", max_results: int = 10) -> List[str]:
    """ 
    Function that given a query it finds it on the intenet
    Args:
        query (str): query to search on internet
        web_browser (str, optional): type of browser, it could be DuckDuckGo or Google,
            default: Google
        max_results (int, optional): maximum number of results

    Returns:
        List[str]: List of strings of web link
    """

    if web_browser == "Google":
        res = []

        for url in search(query, stop=max_results):
            res.append(url)
        return res
    elif web_browser == "DuckDuckGo":
        research = DuckDuckGoSearchResults(max_results=max_results)
        res = research.run(query)

        links = re.findall(r'https?://\S+', res)

        return links
    raise ValueError(
        "The only web browsers avaiable are DuckDuckGo or Google")
