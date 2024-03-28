""" 
Module for making the request on the web
"""
import re
from langchain_community.tools import DuckDuckGoSearchResults


def search_word_on_google(word, max_results=10):
    """ 
    Function that given a word it finds it on the intenet
    Args:
    word (str): word to search on internet
    max_results (int): maximum number of results
    """

    search = DuckDuckGoSearchResults(max_results=max_results)
    res = search.run(word)

    links = re.findall(r'https?://\S+', res)

    return links
