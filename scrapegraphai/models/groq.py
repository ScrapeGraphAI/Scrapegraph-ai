"""
Groq module configuration
"""

from langchain_groq import ChatGroq


class Groq(ChatGroq):
    """Class for wrapping Groq module"""

    def __init__(self, llm_config: dict):
        """
        A wrapper for the Groq class that provides default configuration
        and could be extended with additional methods if needed.

        Args:
            llm_config (dict): Configuration parameters for the language model.
            such as model="llama3-70b-8192" and api_key
        """
        # Initialize the superclass (ChatOpenAI) with provided config parameters
        super().__init__(**llm_config)