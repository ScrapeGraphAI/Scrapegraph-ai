"""
Claude Module
"""

from langchain_anthropic import ChatAnthropic


class Claude(ChatAnthropic):
    """
     A wrapper for the ChatAnthropic class that provides default configuration
    and could be extended with additional methods if needed.

    Args:
        llm_config (dict): Configuration parameters for the language model
                        (e.g., model="claude_instant")
    """

    def __init__(self, llm_config: dict):
        super().__init__(**llm_config)
