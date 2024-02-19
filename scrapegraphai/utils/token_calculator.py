""" 
Module for truncatinh in chunks the messages
"""
from typing import List
import tiktoken

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

def truncate_text_tokens(text: str, model: str, encoding_name: str) -> List[str]:
    """
    It creates a list of strings to create max dimension tokenizable elements

    Args:
        text (str): The input text to be truncated into tokenizable elements.
        model (str): The name of the language model to be used.
        encoding_name (str): The name of the encoding to be used (default: EMBEDDING_ENCODING).

    Returns:
        List[str]: A list of tokenizable elements created from the input text.
    """

    encoding = tiktoken.get_encoding(encoding_name)
    max_tokens = models_tokens[model] - 500
    encoded_text = encoding.encode(text)

    chunks = [encoded_text[i:i + max_tokens]
              for i in range(0, len(encoded_text), max_tokens)]

    result = [encoding.decode(chunk) for chunk in chunks]

    return result
