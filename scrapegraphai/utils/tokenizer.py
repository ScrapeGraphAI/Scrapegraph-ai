"""
Module for counting tokens and splitting text into chunks
"""

from .tokenizers.tokenizer_openai import num_tokens_openai


def num_tokens_calculus(string: str) -> int:
    """
    Returns the number of tokens in a text string.
    """

    num_tokens_fn = num_tokens_openai

    num_tokens = num_tokens_fn(string)
    return num_tokens
