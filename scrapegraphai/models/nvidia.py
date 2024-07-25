""" 
This is a Python wrapper class for ChatNVIDIA. 
It provides default configuration and could be extended with additional methods if needed.
The purpose of this wrapper is to simplify the creation of instances of ChatNVIDIA by providing
default configurations for certain parameters, 
allowing users to focus on specifying other important parameters without having
to understand all the details of the underlying class's constructor.
It inherits from the base class ChatNVIDIA and overrides 
its init method to provide a more user-friendly interface. 
The constructor takes one argument: llm_config, which is used to initialize the superclass 
with default configuration. 
"""

from langchain_nvidia_ai_endpoints import ChatNVIDIA

class Nvidia(ChatNVIDIA): 
    """ A wrapper for the Nvidia class that provides default configuration 
    and could be extended with additional methods if needed.

    Args:
        llm_config (dict): Configuration parameters for the language model.
    """

    def __init__(self, llm_config: dict):
        super().__init__(**llm_config)
