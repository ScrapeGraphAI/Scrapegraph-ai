"""
Module for the ImageToTextNode class.
"""
from typing import List
from .base_node import BaseNode


class ImageToTextNode(BaseNode):
    """
    A class representing a node that processes an image and returns the text description.

    Attributes:
        llm_model (OpenAIImageToText): An instance of the OpenAIImageToText class.

    Methods:
        execute(state, url): Execute the node's logic and return the updated state.
    """

    def __init__(self, input: str, output: List[str], node_config: dict,
                 node_name: str = "ImageToText"):
        """
        Initializes an instance of the ImageToTextNode class.

        Args:
            input (str): The input for the node.
            output (List[str]): The output of the node.
            node_config (dict): Configuration for the model.
            node_name (str): Name of the node.
        """
        super().__init__(node_name, "node", input, output, 1, node_config)
        self.llm_model = node_config["llm_model"]
        self.verbose = True if node_config is None else node_config.get("verbose", False)

    def execute(self, state: dict) -> dict:
        """
        Execute the node's logic and return the updated state.

        Args:
            state (dict): The current state of the graph.

        Returns:
            dict: The updated state after executing this node.
        """

        if self.verbose:
            print("---GENERATING TEXT FROM IMAGE---")
            
        input_keys = self.get_input_keys(state)
        input_data = [state[key] for key in input_keys]
        url = input_data[0]

        text_answer = self.llm_model.run(url)

        state.update({"image_text": text_answer})
        return state
