"""
Tokenization utilities for OpenAI models
"""
import tiktoken
from langchain_core.language_models.chat_models import BaseChatModel
from ..logging import get_logger

def num_tokens_openai(text: str, llm_model:BaseChatModel) -> int:
    """
    Estimate the number of tokens in a given text using OpenAI's tokenization method,
    adjusted for different OpenAI models.

    Args:
        text (str): The text to be tokenized and counted.
        llm_model (BaseChatModel): The specific OpenAI model to adjust tokenization.

    Returns:
        int: The number of tokens in the text.
    """

    logger = get_logger()

    logger.debug(f"Counting tokens for text of {len(text)} characters")
    try:
        model = llm_model.model_name
    except AttributeError:
        raise NotImplementedError(f"The model provider you are using ('{llm_model}') "
            "does not give us a model name so we cannot identify which encoding to use")

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        raise NotImplementedError(f"Tiktoken does not support identifying the encoding for "
            "the model '{model}'")
    
    num_tokens = len(encoding.encode(text))
    return num_tokens
