"""
ImageToTextNode Module
"""

from typing import List, Optional
from .base_node import BaseNode


class ImageToTextNode(BaseNode):
    """
    Retrieve images from a list of URLs and return a description of the images using an image-to-text model.

    Attributes:
        llm_model: An instance of the language model client used for image-to-text conversion.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "ImageToText".
    """

    def __init__(
            self,
            input: str,
            output: List[str],
            node_config: Optional[dict]=None,
            node_name: str = "ImageToText",
        ):
        super().__init__(node_name, "node", input, output, 1, node_config)

        self.llm_model = node_config["llm_model"]
        self.verbose = False if node_config is None else node_config.get("verbose", False)
        self.max_images = 5 if node_config is None else node_config.get("max_images", 5)

    def execute(self, state: dict) -> dict:
        """
        Generate text from an image using an image-to-text model. The method retrieves the image
        from the list of URLs provided in the state and returns the extracted text.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data types from the state.

        Returns:
            dict: The updated state with the input key containing the text extracted from the image.
        """

        if self.verbose:
            print(f"--- Executing {self.node_name} Node ---")
            
        input_keys = self.get_input_keys(state)
        input_data = [state[key] for key in input_keys]
        urls = input_data[0]

        if isinstance(urls, str):
            urls = [urls]
        elif len(urls) == 0:
            return state

        # Skip the image-to-text conversion
        if self.max_images < 1:
            return state
        
        img_desc = []
        for url in urls[:self.max_images]:
            try:
                text_answer = self.llm_model.run(url)
            except Exception as e:
                text_answer = f"Error: incompatible image format or model failure."
            img_desc.append(text_answer)

        state.update({self.output[0]: img_desc})
        return state
