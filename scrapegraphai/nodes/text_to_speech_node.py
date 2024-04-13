
"""
Module for parsing the text to voice
"""
from typing import List, Dict
from .base_node import BaseNode


class TextToSpeechNode(BaseNode):
    """
    A class representing a node that processes text and returns the voice.

    Attributes:
        llm (OpenAITextToSpeech): An instance of the OpenAITextToSpeech class.

    Methods:
        execute(state, text): Execute the node's logic and return the updated state.
    """

    def __init__(self, input: str, output: List[str],
                 node_config: dict, node_name: str = "TextToSpeech"):
        """
        Initializes an instance of the TextToSpeechNode class.
        """
        super().__init__(node_name, "node", input, output, 1, node_config)
        self.tts_model = node_config["tts_model"]

    def execute(self, state: List[Dict]) -> List[Dict]:
        """
        Execute the node's logic and return the updated state.
        Args:
            state (dict): The current state of the graph.
            text (str): The text to convert to speech.

        Returns:
            List[Dict]: The updated state after executing this node.
        """

        print(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state[-1])

        # Fetching data from the state based on the input keys
        input_data = [state[-1][key] for key in input_keys]

        # get the text to translate
        text2translate = str(next(iter(input_data[0].values())))
        # text2translate = str(input_data[0])

        audio = self.tts_model.run(text2translate)

        state.append({self.output[0]: audio})
        return state
