""" 
Module for truncatinh in chunks the messages
"""
from typing import List
import tiktoken
from ..helpers.models_tokens import models_tokens


def truncate_text_tokens(text: str, model: str, encoding_name: str) -> List[str]:
    """
    Truncates text into chunks that are small enough to be processed by specified llm models.

    Args:
        text (str): The input text to be truncated.
        model (str): The name of the llm model to determine the maximum token limit.
        encoding_name (str): The encoding strategy used to encode the text before truncation.

    Returns:
        List[str]: A list of text chunks, each within the token limit of the specified model.

    Example:
        >>> truncate_text_tokens("This is a sample text for truncation.", "GPT-3", "EMBEDDING_ENCODING")
        ["This is a sample text", "for truncation."]

    This function ensures that each chunk of text can be tokenized by the specified model without exceeding the model's token limit.
    """

    encoding = tiktoken.get_encoding(encoding_name)
    max_tokens = models_tokens[model] - 500
    encoded_text = encoding.encode(text)

    chunks = [encoded_text[i:i + max_tokens]
              for i in range(0, len(encoded_text), max_tokens)]

    result = [encoding.decode(chunk) for chunk in chunks]

    return result
