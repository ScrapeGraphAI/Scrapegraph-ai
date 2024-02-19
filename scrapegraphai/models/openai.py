""" 
openai configuration wrapper
"""
from langchain_openai import ChatOpenAI


class OpenAI(ChatOpenAI):
    """Class for wrapping openai module"""

    def __init__(self, llm_config: dict):
        """
        A wrapper for the ChatOpenAI class that provides default configuration
        and could be extended with additional methods if needed.

        Args:
            llm_config (dict): Configuration parameters for the language model.
        """
        # Initialize the superclass (ChatOpenAI) with provided config parameters
        super().__init__(**llm_config)
