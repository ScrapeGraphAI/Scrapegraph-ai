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

    def __init__(self, input: str, output: List[str], model_config: dict,
                 node_name: str = "GetProbableTags"):
        """
        Initializes an instance of the ImageToTextNode class.

        Args:
            input (str): The input for the node.
            output (List[str]): The output of the node.
            model_config (dict): Configuration for the model.
            node_name (str): Name of the node.
        """
        super().__init__(node_name, "node", input, output, 2, model_config)
        self.llm_model = model_config["llm_model"]

    def execute(self, state: dict, url: str) -> dict:
        """
        Execute the node's logic and return the updated state.

        Args:
            state (dict): The current state of the graph.
            url (str): URL of the image to process.

        Returns:
            dict: The updated state after executing this node.
        """
        print("---GENERATING TEXT FROM IMAGE---")
        text_answer = self.llm_model.run(url)

        state.update({"image_text": text_answer})
        return state
