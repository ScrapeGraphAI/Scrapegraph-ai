
"""
Module for parsing the text to voice
"""

from .base_node import BaseNode
from typing import List

class TextToSpeechNode(BaseNode):
    """
    A class representing a node that processes text and returns the voice.

    Attributes:
        llm (OpenAITextToSpeech): An instance of the OpenAITextToSpeech class.

    Methods:
        execute(state, text): Execute the node's logic and return the updated state.
    """

    def __init__(self, input: str, output: List[str], model_config: dict, node_name: str = "TextToSpeechNode"):
        """
        Initializes an instance of the TextToSpeechNode class.
        """
        super().__init__(node_name, "node", input, output, 1, model_config)
        self.text2speech_model = model_config["text2speech_model"]

    def execute(self, state):
        """
        Execute the node's logic and return the updated state.
        Args:
            state (dict): The current state of the graph.
            text (str): The text to convert to speech.

        :return: The updated state after executing this node.
        """

        print(f"--- Executing {self.node_name} Node ---")
    
        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)
        
        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        text2translate = input_data[0]

        # if not a string, raise an error
        if not isinstance(text2translate, str):
            raise ValueError("No text to translate to speech.")
        print("---TRANSLATING TEXT TO SPEECH---")
        audio = self.text2speech_model.run(text2translate["summary"])

        state.update({self.output[0]: audio})
        return state
