"""
Module for implementing the hugginface class
"""
from langchain_community.chat_models.huggingface import ChatHuggingFace


class HuggingFace(ChatHuggingFace):
    """Provides a convenient wrapper for interacting with Hugging Face language models
    designed for conversational AI applications.

    Args:
        llm_config (dict): A configuration dictionary containing:
            * api_key (str, optional): Your Hugging Face API key.
            * model_name (str): The name of the Hugging Face LLM to load.
            * tokenizer_name (str, optional):  Name of the corresponding tokenizer.
            * device (str, optional): Device for running the model ('cpu' by default).

    """

    def __init__(self, llm_config: dict):
        """Initializes the HuggingFace chat model wrapper"""
        super().__init__(**llm_config)
