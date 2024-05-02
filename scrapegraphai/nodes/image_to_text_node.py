"""
ImageToTextNode Module
"""

from typing import List
from .base_node import BaseNode


class ImageToTextNode(BaseNode):
    """
    Retrieve an image from an URL and convert it to text using an ImageToText model.

    Attributes:
        llm_model: An instance of the language model client used for image-to-text conversion.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "ImageToText".
    """

    def __init__(self, input: str, output: List[str], node_config: dict,
                 node_name: str = "ImageToText"):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.llm_model = node_config["llm_model"]
        self.verbose = True if node_config is None else node_config.get("verbose", False)

    def execute(self, state: dict) -> dict:
        """
        Generate text from an image using an image-to-text model. The method retrieves the image
        from the URL provided in the state.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data types from the state.

        Returns:
            dict: The updated state with the input key containing the text extracted from the image.
        """

        if self.verbose:
            print("---GENERATING TEXT FROM IMAGE---")
            
        input_keys = self.get_input_keys(state)
        input_data = [state[key] for key in input_keys]
        url = input_data[0]

        text_answer = self.llm_model.run(url)

        state.update({"image_text": text_answer})
        return state
