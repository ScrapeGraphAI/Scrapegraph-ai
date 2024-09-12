"""
Tokenization utilities for Mistral models
"""
from mistral_common.protocol.instruct.messages import UserMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest
from mistral_common.protocol.instruct.tool_calls import Function, Tool
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from langchain_core.language_models.chat_models import BaseChatModel
from ..logging import get_logger


def num_tokens_mistral(text: str, llm_model:BaseChatModel) -> int:
    """
    Estimate the number of tokens in a given text using Mistral's tokenization method,
    adjusted for different Mistral models.

    Args:
        text (str): The text to be tokenized and counted.
        llm_model (BaseChatModel): The specific Mistral model to adjust tokenization.

    Returns:
        int: The number of tokens in the text.
    """

    logger = get_logger()

    logger.debug(f"Counting tokens for text of {len(text)} characters")
    try:
        model = llm_model.model
    except AttributeError:
        raise NotImplementedError(f"The model provider you are using ('{llm_model}') "
            "does not give us a model name so we cannot identify which encoding to use")

    tokenizer = MistralTokenizer.from_model(model)

    tokenized = tokenizer.encode_chat_completion(
        ChatCompletionRequest(
            tools=[],
            messages=[
                UserMessage(content=text),
            ],
            model=model,
        )
    )
    tokens = tokenized.tokens
    return len(tokens)
