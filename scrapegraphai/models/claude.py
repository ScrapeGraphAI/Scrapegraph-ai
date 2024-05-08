"""
Claude model
"""
from langchain_anthropic import ChatAnthropic


class Claude(ChatAnthropic):
    """Class for wrapping bedrock module"""

    def __init__(self, llm_config: dict):
        """
        A wrapper for the Claude class that provides default configuration
        and could be extended with additional methods if needed.

        Args:
            llm_config (dict): Configuration parameters for the language model.
        """
        # Initialize the superclass (ChatAnthropic) with provided config parameters
        super().__init__(**llm_config)
