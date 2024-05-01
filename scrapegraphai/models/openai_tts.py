"""
OpenAITextToSpeech Module
"""

from openai import OpenAI


class OpenAITextToSpeech:
    """
    Implements a text-to-speech model using the OpenAI API.

    Attributes:
        client (OpenAI): The OpenAI client used to interact with the API.
        model (str): The model to use for text-to-speech conversion.
        voice (str): The voice model to use for generating speech.

    Args:
        tts_config (dict): Configuration parameters for the text-to-speech model.
    """

    def __init__(self, tts_config: dict):

        # convert model_name to model
        self.client = OpenAI(api_key=tts_config.get("api_key"))
        self.model = tts_config.get("model", "tts-1")
        self.voice = tts_config.get("voice", "alloy")

    def run(self, text: str) -> bytes:
        """
        Converts the provided text to speech and returns the bytes of the generated speech.

        Args:
            text (str): The text to convert to speech.

        Returns:
            bytes: The bytes of the generated speech audio.
        """
        response = self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text
        )

        return response.content
