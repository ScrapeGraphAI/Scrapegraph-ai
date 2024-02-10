from langchain_community.document_loaders import AsyncHtmlLoader 
from langchain_community.document_transformers import Html2TextTransformer

def get_function(link:str) -> str:
    """
    It sends a GET request to the specified link with optional headers.

    Args:
        link (str): The URL to send the GET request to.

    Returns:
        str: The content of the response as a string.
    """
    loader = AsyncHtmlLoader(link) 
    print(str(loader.load()))
    return str(loader.load())
