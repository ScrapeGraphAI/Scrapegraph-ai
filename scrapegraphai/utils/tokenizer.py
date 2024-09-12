"""
Module for calculting the token_for_openai
"""
import tiktoken

def num_tokens_calculus(string: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(string))
    return num_tokens
