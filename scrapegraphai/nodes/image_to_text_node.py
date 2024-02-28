""" 
Module for the ImageToTextNode class.
"""

from .base_node import BaseNode


class ImageToTextNode(BaseNode):
    """
    A class representing a node that processes an image and returns the text description.

    Attributes:
        llm (OpenAIImageToText): An instance of the OpenAIImageToText class.

    Methods:
        execute(state, url): Execute the node's logic and return the updated state.
    """

    def __init__(self, llm, node_name: str, node_type: str = "ImageToTextNode"):
        """
        Initializes an instance of the ImageToTextNode class.

        Args:
            llm (OpenAIImageToText): An instance of the OpenAIImageToText class.
            node_name (str): name of the node
            node_type (str, optional): type of the node
        """
        super().__init__(node_name, "node")
        self.llm = llm

    def execute(self, state: dict, url: str) -> dict:
        """
        Execute the node's logic and return the updated state.
        Args:
            state (dict): The current state of the graph.
            url (str): url of the image where to 
        :return: The updated state after executing this node.
        """

        print("---GENERATING TEXT FROM IMAGE---")
        text_answer = self.llm.run(url)

        state.update({"image_text": text_answer})
        return state
