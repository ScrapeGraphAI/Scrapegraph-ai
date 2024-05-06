"""
TextToSpeechNode Module
"""

from typing import List, Optional
from .base_node import BaseNode


class TextToSpeechNode(BaseNode):
    """
    Converts text to speech using the specified text-to-speech model.

    Attributes:
        tts_model: An instance of the text-to-speech model client.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "TextToSpeech".
    """

    def __init__(self, input: str, output: List[str],
                 node_config: Optional[dict]=None, node_name: str = "TextToSpeech"):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.tts_model = node_config["tts_model"]
        self.verbose = True if node_config is None else node_config.get("verbose", False)

    def execute(self, state: dict) -> dict:
        """
        Converts text to speech using the specified text-to-speech model.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data types from the state.
                            
        Returns:
            dict: The updated state with the output key containing the audio generated from the text.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for generating the audio is missing.
        """

        if self.verbose:
            print(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        # get the text to translate
        text2translate = str(next(iter(input_data[0].values())))
        # text2translate = str(input_data[0])

        audio = self.tts_model.run(text2translate)

        state.update({self.output[0]: audio})
        return state
