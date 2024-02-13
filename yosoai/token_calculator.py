"""
Module for calculating token truncation for text
"""
from typing import List
from tiktoken import tokenizer


def truncate_text_tokens(text: str, model: str, encoding_name: str) -> List[str]:
    """
    Truncates the input text into smaller chunks based on the model's token limit.
    Args:
        text (str): The input text to be truncated.
        model (str): The name of the language model.
        encoding_name (str): The name of the encoding to be used.
    Returns:
        List[str]: A list of truncated text chunks.
    """
    # Calculate the token limit for the given model and encoding
    token_limit = tokenizer.token_limit(model, encoding_name)
    # Truncate the text into smaller chunks based on the token limit
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start:start+token_limit]
        chunks.append(chunk)
        start += token_limit
    return chunks
