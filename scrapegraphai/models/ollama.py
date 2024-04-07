""" 
openai configuration wrapper
"""
from langchain_community.chat_models import ChatOllama


class Ollama(ChatOllama):
    """Class for wrapping ollama module"""

    def __init__(self, llm_config: dict):
        """
        A wrapper for the ChatOllama class that provides default configuration
        and could be extended with additional methods if needed.

        Args:
            llm_config (dict): Configuration parameters for the language model.
        """
        # Initialize the superclass (ChatOllama) with provided config parameters
        super().__init__(**llm_config)
