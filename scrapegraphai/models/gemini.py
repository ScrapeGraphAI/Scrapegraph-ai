from langchain_google_genai import ChatGoogleGenerativeAI


class Gemini(ChatGoogleGenerativeAI):
    """Class for wrapping gemini module"""

    def __init__(self, llm_config: dict):
        """
        A wrapper for the Gemini class that provides default configuration
        and could be extended with additional methods if needed.

        Args:
            llm_config (dict): Configuration parameters for the language model.
            such as model="gemini-pro" and api_key 
        """
        # change the key model_name to model
        llm_config["model"] = llm_config["model_name"]
        # Initialize the superclass (ChatOpenAI) with provided config parameters
        super().__init__(**llm_config)
