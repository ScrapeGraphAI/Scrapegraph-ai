"""
Tokenization utilities for Ollama models
"""
from langchain_core.language_models.chat_models import BaseChatModel
from ..logging import get_logger

def num_tokens_ollama(text: str, llm_model:BaseChatModel) -> int:
    """
    Estimate the number of tokens in a given text using Ollama's tokenization method,
    adjusted for different Ollama models.

    Args:
        text (str): The text to be tokenized and counted.
        llm_model (BaseChatModel): The specific Ollama model to adjust tokenization.

    Returns:
        int: The number of tokens in the text.
    """

    logger = get_logger()

    logger.debug(f"Counting tokens for text of {len(text)} characters")

    # Use langchain token count implementation
    # NB: https://github.com/ollama/ollama/issues/1716#issuecomment-2074265507
    tokens = llm_model.get_num_tokens(text)
    return tokens

