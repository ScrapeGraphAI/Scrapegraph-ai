""" 
Module for FetchTextNode
"""
from langchain_core.documents import Document
from .base_node import BaseNode


class FetchTextNode(BaseNode):
    """
    A node for loading raw text into the state.

    Primarily used in scraping workflows, this node prepares the state by directly 
    loading raw text content from a specified source, making it available for 
    further processing by subsequent nodes in the graph.

    Attributes:
      node_name (str): The unique identifier for the node.
      node_type (str): The type of the node ("node" in this case).

    Args:
      node_name (str): The unique identifier for the node.

    Methods:
      execute(state): Directly loads text content into the state and stores it
          under the 'document' key. Requires the 'url' key to be present in 
          the state, representing the location of the text content.
    """

    def __init__(self, node_name: str):
        """
        Initializes the FetchTextNode with a node name.

        Args:
          node_name (str): The unique name for the node.
        """
        super().__init__(node_name, "node")

    def execute(self, state: dict) -> dict:
        """
        Loads raw text content into the state.

        Args:
          state (dict): The current state, expected to contain a 'text' key 
              indicating the source of the text.

        Returns:
          dict: The updated state with the text content stored under the 'document' key.

        Raises:
          KeyError: If the 'url' key is missing from the state.
        """
        print("---LOADING TEXT CODE---")

        if 'text' not in state:
            raise KeyError("The 'url' key is required to load the text.")

        state["document"] = Document(page_content=state["text"])
        return state
