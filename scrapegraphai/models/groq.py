"""
Groq Module
"""

from langchain_groq import ChatGroq

class Groq(ChatGroq):
    """
    A wrapper for the Groq class that provides default configuration
    and could be extended with additional methods if needed.

    Args:
        llm_config (dict): Configuration parameters for the language model (e.g., model="llama3-70b-8192")
    """

    def __init__(self, llm_config: dict):
        super().__init__(**llm_config)