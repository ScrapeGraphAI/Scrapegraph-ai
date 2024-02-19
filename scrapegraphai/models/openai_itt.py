"""
This module contains the OpenAIImageToText class, which is a subclass of ChatOpenAI that is specialized for converting images to text.
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

class OpenAIImageToText(ChatOpenAI):
    """
    A class that uses OpenAI's Chat API to convert an image to text.

    Args:
        llm_config (dict): The configuration for the language model.

    Attributes:
        max_tokens (int): The maximum number of tokens to generate in the response.

    Methods:
        run(image_url): Runs the image-to-text conversion using the provided image URL.

    """

    def __init__(self, llm_config: dict):
        """
        Initializes an instance of the OpenAIImageToText class.

        Args:
            llm_config (dict): The configuration for the language model.

        """
        super().__init__(**llm_config, max_tokens=256)

    def run(self, image_url: str):
        """
        Runs the image-to-text conversion using the provided image URL.

        Args:
            image_url (str): The URL of the image to convert to text.

        Returns:
            str: The generated text description of the image.

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

        # Use the invoke method from the superclass (ChatOpenAI)
        result = self.invoke([message]).content
        
        return result
