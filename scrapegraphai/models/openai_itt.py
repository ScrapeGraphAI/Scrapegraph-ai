"""
OpenAIImageToText Module
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

class OpenAIImageToText(ChatOpenAI):
    """
    A wrapper for the OpenAIImageToText class that provides default configuration
    and could be extended with additional methods if needed.

    Args:
        llm_config (dict): Configuration parameters for the language model.
        max_tokens (int): The maximum number of tokens to generate.

    """

    def __init__(self, llm_config: dict):
        super().__init__(**llm_config, max_tokens=256)

    def run(self, image_url: str) -> str:
        """
        Runs the image-to-text conversion using the provided image URL.

        Args:
            image_url (str): The URL of the image to convert.

        Returns:
            str: The text description of the image.
        """
        message = HumanMessage(
            content=[
                {"type": "text", "text": "What is this image showing"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url,
                        "detail": "auto",
                    },
                },
            ]
        )

        result = self.invoke([message]).content
        return result
