"""
Module for retrieving content from a URL
"""
from langchain_community.document_loaders import AsyncHtmlLoader


def _get_function(link: str) -> str:
    """
    It sends a GET request to the specified link with optional headers.

    Args:
        link (str): The URL to send the GET request to.

    Returns:
        str: The content of the response as a string.
    """
    loader = AsyncHtmlLoader(link)
    return str(loader.load())
