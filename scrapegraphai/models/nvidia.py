"""
NVIDIA Module
"""


class Nvidia:
    """
    A wrapper for the ChatNVIDIA class that provides default configuration
    and could be extended with additional methods if needed.

    Note: This class uses __new__ instead of __init__ because langchain_nvidia_ai_endpoints
    is an optional dependency. We cannot inherit from ChatNVIDIA at class definition time
    since the module may not be installed. The __new__ method allows us to lazily import
    and return a ChatNVIDIA instance only when Nvidia() is instantiated.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __new__(cls, **llm_config):
        try:
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
        except ImportError:
            raise ImportError(
                """The langchain_nvidia_ai_endpoints module is not installed.
                              Please install it using `pip install langchain-nvidia-ai-endpoints`."""
            )

        if "api_key" in llm_config:
            llm_config["nvidia_api_key"] = llm_config.pop("api_key")

        return ChatNVIDIA(**llm_config)
