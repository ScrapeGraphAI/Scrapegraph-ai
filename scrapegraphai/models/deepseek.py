""" 
DeepSeek Module
"""
from langchain_openai import ChatOpenAI


class DeepSeek(ChatOpenAI):
    """
    A wrapper for the ChatOpenAI class (DeepSeek uses an OpenAI-like API) that
    provides default configuration and could be extended with additional methods
    if needed.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if 'api_key' in llm_config:
            llm_config['openai_api_key'] = llm_config.pop('api_key')
        llm_config['openai_api_base'] = 'https://api.deepseek.com/v1'

        super().__init__(**llm_config)
