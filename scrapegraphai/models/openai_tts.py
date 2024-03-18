"""
This module contains the OpenAITextToSpeech class, which uses OpenAI's API
to convert text into speech.
"""

from openai import OpenAI


class OpenAITextToSpeech:
    """
    A class that uses OpenAI's API to convert text to speech.

    Args:
        llm_config (dict): The configuration for the language model.

    Attributes:
        model (str): The model to use for text-to-speech conversion.
        voice (str): The voice model to use for generating speech.

    Methods:
        run(text): Converts the provided text to speech and returns the
        bytes of the generated speech.
    """

    def __init__(self, tts_config: dict):
        """
        Initializes an instance of the OpenAITextToSpeech class.

        Args:
            llm_config (dict): The configuration for the language model.
            model (str, optional): The model to use for text-to-speech conversion. 
            Defaults to "tts-1".
            voice (str, optional): The voice model to use for generating speech. 
            Defaults to "alloy".
        """

        # convert model_name to model
        self.client = OpenAI(api_key=tts_config.get("api_key"))
        self.model = tts_config.get("model", "tts-1")
        self.voice = tts_config.get("voice", "alloy")

    def run(self, text):
        """
        Converts the provided text to speech and returns the bytes of the generated speech.

        Args:
            text (str): The text to convert to speech.

        """
        response = self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text
        )

        return response.content
