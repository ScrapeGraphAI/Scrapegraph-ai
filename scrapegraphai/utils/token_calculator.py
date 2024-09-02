""" 
Module for truncating in chunks the messages
"""
from typing import List
import tiktoken
from ..helpers.models_tokens import models_tokens


def truncate_text_tokens(text: str, model: str) -> List[str]:
    """
    Truncates text into chunks that are small enough to be processed by specified llm models.

    Args:
        text (str): The input text to be truncated.
        model (str): The name of the llm model to determine the maximum token limit.

    Returns:
        List[str]: A list of text chunks, each within the token limit of the specified model.

    Example:
        >>> truncate_text_tokens("This is a sample text for truncation.", "gpt-4o-mini")
        ["This is a sample text", "for truncation."]

    This function ensures that each chunk of text can be tokenized 
    by the specified model without exceeding the model's token limit.
    """

    encoding = tiktoken.encoding_for_model(model)
    max_tokens = min(models_tokens[model] - 500, int(models_tokens[model] * 0.9))
    encoded_text = encoding.encode(text)

    chunks = [encoded_text[i:i + max_tokens]
              for i in range(0, len(encoded_text), max_tokens)]

    result = [encoding.decode(chunk) for chunk in chunks]

    return result


def token_count(text: str, model: str) -> List[str]:
    """
    Return the number of tokens within the text, based on the encoding of the specified model.

    Args:
        text (str): The input text to be counted.
        model (str): The name of the llm model to determine the encoding.

    Returns:
        int: Number of tokens.

    Example:
        >>> token_count("This is a sample text for counting.", "gpt-4o-mini")
        9

    This function ensures that each chunk of text can be tokenized 
    by the specified model without exceeding the model's token limit.
    """

    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(text))

    return num_tokens
