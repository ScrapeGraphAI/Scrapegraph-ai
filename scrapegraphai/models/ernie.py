""" 
Ollama Module
"""
from langchain_community.chat_models import ErnieBotChat


class Ernie(ErnieBotChat):
    """
    A wrapper for the ErnieBotChat class that provides default configuration
    and could be extended with additional methods if needed.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, llm_config: dict):
        super().__init__(**llm_config)
