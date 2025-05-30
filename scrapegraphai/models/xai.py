"""
xAI Grok Module
"""
from langchain_groq import ChatGroq as LangchainChatGroq

class XAI(LangchainChatGroq):
    """
    Wrapper for the ChatGroq class from langchain_groq, for use with xAI models.
    Handles API key mapping from generic 'api_key' to 'groq_api_key' and
    maps 'model' to 'model_name'.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, **llm_config):
        if "api_key" in llm_config and "groq_api_key" not in llm_config:
            llm_config["groq_api_key"] = llm_config.pop("api_key")
        
        if "model" in llm_config and "model_name" not in llm_config:
            llm_config["model_name"] = llm_config.pop("model")

        super().__init__(**llm_config) 