""" 
Module for truncating in chunks the messages
"""
from typing import List
import tiktoken
from ..helpers.models_tokens import models_tokens
from langchain_core.language_models.chat_models import BaseChatModel
from .logging import get_logger

def truncate_text_tokens(text: str, llm_model: BaseChatModel) -> List[str]:
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

    logger = get_logger()

    try:
        model = llm_model.model_name
    except AttributeError:
        logger.warning(f"The model provider you are using ('{llm_model}') "
            "does not give a model name so we need to guess the right encoding "
            "to use")
        model = 'gpt-4o-mini'

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning(f"Tiktoken does not support identifying the encoding for "
            "the model '{model}', using OpenAI encoding instead as a workaround. "
            "Token count will be incorrect as a result.")
        encoding = tiktoken.encoding_for_model('gpt-4o-mini')

    max_tokens = min(models_tokens[model] - 500, int(models_tokens[model] * 0.9))
    encoded_text = encoding.encode(text)

    chunks = [encoded_text[i:i + max_tokens]
              for i in range(0, len(encoded_text), max_tokens)]

    result = [encoding.decode(chunk) for chunk in chunks]

    return result


def token_count(text: str, llm_model: BaseChatModel) -> List[str]:
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
    logger = get_logger()

    logger.debug(f"Counting tokens for text of {len(text)} characters")
    try:
        model = llm_model.model_name
    except AttributeError:
        logger.warning(f"The model provider you are using ('{llm_model}') "
            "does not give a model name so we need to guess the right encoding "
            "to use")
        model = 'gpt-4o-mini'

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning(f"Tiktoken does not support identifying the encoding for "
            "the model '{model}', using OpenAI encoding instead as a workaround. "
            "Token count will be incorrect as a result.")
        encoding = tiktoken.encoding_for_model('gpt-4o-mini')
    num_tokens = len(encoding.encode(text))

    logger.debug(f"Token count is {num_tokens}")
    return num_tokens
