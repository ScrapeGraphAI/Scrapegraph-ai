import tiktoken
from typing import List
from .dictionaries import models_tokens 

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
    
    chunks = [encoded_text[i:i + max_tokens] for i in range(0, len(encoded_text), max_tokens)]
    
    result = [encoding.decode(chunk) for chunk in chunks]
    
    return result
    