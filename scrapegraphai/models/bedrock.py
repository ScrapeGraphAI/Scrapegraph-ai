""" 
bedrock configuration wrapper
"""
from langchain_aws import ChatBedrock


class Bedrock(ChatBedrock):
    """Class for wrapping bedrock module"""

    def __init__(self, llm_config: dict):
        """
        A wrapper for the ChatBedrock class that provides default configuration
        and could be extended with additional methods if needed.

        Args:
            llm_config (dict): Configuration parameters for the language model.
        """
        # Initialize the superclass (ChatBedrock) with provided config parameters
        super().__init__(**llm_config)
