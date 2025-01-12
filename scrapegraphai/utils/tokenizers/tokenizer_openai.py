"""
Tokenization utilities for OpenAI models
"""

import tiktoken

from ..logging import get_logger


def num_tokens_openai(text: str) -> int:
    """
    Estimate the number of tokens in a given text using OpenAI's tokenization method,
    adjusted for different OpenAI models.

    Args:
        text (str): The text to be tokenized and counted.

    Returns:
        int: The number of tokens in the text.
    """

    logger = get_logger()

    logger.debug(f"Counting tokens for text of {len(text)} characters")

    encoding = tiktoken.encoding_for_model("gpt-4o")

    num_tokens = len(encoding.encode(text))
    return num_tokens
