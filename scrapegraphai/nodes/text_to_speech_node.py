
"""
Module for parsing the text to voice
"""

from .base_node import BaseNode


class TextToSpeechNode(BaseNode):
    """
    A class representing a node that processes text and returns the voice.

    Attributes:
        llm (OpenAITextToSpeech): An instance of the OpenAITextToSpeech class.

    Methods:
        execute(state, text): Execute the node's logic and return the updated state.
    """

    def __init__(self, llm, node_name: str = "TextToSpeechNode"):
        """
        Initializes an instance of the TextToSpeechNode class.
        """
        super().__init__(node_name, "node")
        self.llm = llm

    def execute(self, state: dict) -> dict:
        """
        Execute the node's logic and return the updated state.
        Args:
            state (dict): The current state of the graph.
            text (str): The text to convert to speech.

        :return: The updated state after executing this node.
        """

        text2translate = state.get("answer", None)
        if not text2translate:
            raise ValueError("No text to translate to speech.")
        print("---TRANSLATING TEXT TO SPEECH---")
        audio = self.llm.run(text2translate["summary"])

        state.update({"audio": audio})
        return state
