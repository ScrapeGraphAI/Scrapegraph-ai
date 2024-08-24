from mistral_common.protocol.instruct.messages import UserMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest
from mistral_common.protocol.instruct.tool_calls import Function, Tool
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer

def num_tokens_mistral(text: str, model_name: str) -> int:
    """
    Estimate the number of tokens in a given text using Mistral's tokenization method,
    adjusted for different Mistral models.

    Args:
        text (str): The text to be tokenized and counted.
        model_name (str): The specific Mistral model name to adjust tokenization.

    Returns:
        int: The number of tokens in the text.
    """
    tokenizer = MistralTokenizer.from_model(model_name)

    tokenized = tokenizer.encode_chat_completion(
        ChatCompletionRequest(
            tools=[],
            messages=[
                UserMessage(content=text),
            ],
            model=model_name,
        )
    )
    tokens = tokenized.tokens
    return len(tokens)
