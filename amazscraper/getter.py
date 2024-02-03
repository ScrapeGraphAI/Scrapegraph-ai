import requests
import tiktoken
from typing import List

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
           'Accept-Language': 'en-US'}

models_tokens = {
    "gpt-3.5-turbo-0125": 16385,
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-1106": 16385,
    "gpt-3.5-turbo-instruct": 4096,
    "gpt-4-0125-preview": 128000,
    "gpt-4-turbo-preview": 128000,
    "gpt-4-1106-preview": 128000,
    "gpt-4-vision-preview": 128000,
    "gpt-4": 8192,
    "gpt-4-0613": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
}

EMBEDDING_ENCODING = 'cl100k_base'

DEFAULT_MESSAGE_LENGTH = 100


def truncate_text_tokens(text: str, model: str, encoding_name: str = EMBEDDING_ENCODING) -> List[str]:
    """
    It creates a list of strings to create max dimension tokenizable elements

    Parameters:
    text (str): text to scrape
    model_name (str): The name of the language model to be used (default: "gpt-3.5-turbo"). All
    the possible models are available at the following link: https://platform.openai.com/docs/models
    encoding_name (str):

    Returns
    List[str] of elements to send the requests
    """
    encoding = tiktoken.get_encoding(encoding_name)
    max_tokens = models_tokens[model]
    encoded_text = encoding.encode(text)
    
    chunks = [encoded_text[i:i + max_tokens] for i in range(0, len(encoded_text), max_tokens)]
    
    result = [encoding.decode(chunk) for chunk in chunks]
    
    return result


def get_function(link:str, param = HEADERS) -> str:
    """
    It sends a GET request to the specified link with optional headers.

    Parameters:
    link (str): The URL to send the GET request to.
    param (dict): Optional headers to include in the request. Default is HEADERS.

    Returns:
    str: The content of the response as a string.
    """
    response = requests.get(url=link, headers=param)
    return str(response.content)

def remover(file:str) -> str:
    '''
    This function elaborate the HTML file and remove all the not necessary tag
    Parameters:
    file (str): the file to parse

    Returns:
    str: the parsed file
    '''
    res = ""
    
    isBody = False

    for elem in file.splitlines():
        if "<title>" in elem:
            res = res + elem

        if "<body>" in elem: 
            isBody = True

        if "</body>" in elem:
            break

        if "<script>" in elem:
            continue

        if isBody == True:
            res = res + elem

    return res.replace("\n", "")
