""" 
Module for counting tokens and splitting text into chunks
"""
from typing import List
import tiktoken
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_mistralai import ChatMistralAI
from ..helpers.models_tokens import models_tokens
from langchain_core.language_models.chat_models import BaseChatModel
from .logging import get_logger

def chunk_text(text: str, llm_model: BaseChatModel, chunk_size: int, use_semchunk=False) -> List[str]:
    """
    Truncates text into chunks that are small enough to be processed by specified llm models.

    Args:
        text (str): The input text to be truncated.
        llm_model (BaseChatModel): The langchain chat model object.
        chunk_size (int): Number of tokens per chunk allowed.
        use_semchunk: Whether to use semchunk to split the text or use a simple token count 
            based approach.

    Returns:
        List[str]: A list of text chunks, each within the token limit of the specified model.

    Example:
        >>> chunk_text("This is a sample text for truncation.", openai_model)
        ["This is a sample text", "for truncation."]

    This function ensures that each chunk of text can be tokenized 
    by the specified model without exceeding the model's token limit.
    """



    if isinstance(llm_model, ChatOpenAI):
        from .tokenizers.tokenizer_openai import num_tokens_openai
        num_tokens_fn = num_tokens_openai

    elif isinstance(llm_model, ChatMistralAI):
        from .tokenizers.tokenizer_mistral import num_tokens_mistral
        num_tokens_fn = num_tokens_mistral

    elif isinstance(llm_model, ChatOllama):
        from .tokenizers.tokenizer_ollama import num_tokens_ollama
        num_tokens_fn = num_tokens_ollama

    else:
        raise NotImplementedError(f"There is no tokenization implementation for model '{llm_model}'")
            

    if use_semchunk:
        def count_tokens(text):
            return token_count_fn(text, llm_model)

        chunk_size = min(chunk_size - 500, int(chunk_size * 0.9))

        chunks = chunk(text=text,
                        chunk_size=chunk_size,
                        token_counter=count_tokens,
                        memoize=False)
        return chunks

    else:
            
        num_tokens = num_tokens_fn(text, llm_model)

        chunks = []
        num_chunks = num_tokens // chunk_size

        if num_tokens % chunk_size != 0:
            num_chunks += 1

        for i in range(num_chunks):
            start = i * chunk_size
            end = (i + 1) * chunk_size
            chunks.append(text[start:end])

        return chunks





    #################
    # previous chunking code
    #################

    #encoding = tiktoken.get_encoding(encoding_name)
    #max_tokens = min(models_tokens[model] - 500, int(models_tokens[model] * 0.9))
    #encoded_text = encoding.encode(text)

    #chunks = [encoded_text[i:i + max_tokens]
    #          for i in range(0, len(encoded_text), max_tokens)]

    #result = [encoding.decode(chunk) for chunk in chunks]

    #return result
