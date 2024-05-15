""" 
BlocksIndentifier Module
"""

from typing import List, Optional
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_core.documents import Document
from .base_node import BaseNode



class BlocksIndentifier(BaseNode):
    """
    A node responsible to identify the blocks in the HTML content of a specified HTML content
    e.g products in a E-commerce, flights in a travel website etc. 

    Attributes:
        headless (bool): A flag indicating whether the browser should run in headless mode.
        verbose (bool): A flag indicating whether to print verbose output during execution.
    
    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (Optional[dict]): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "BlocksIndentifier".
    """

    def __init__(self, input: str, output: List[str], node_config: Optional[dict], node_name: str = "BlocksIndentifier"):
        super().__init__(node_name, "node", input, output, 1)

        self.headless = True if node_config is None else node_config.get("headless", True)
        self.verbose = True if node_config is None else node_config.get("verbose", False)

    def execute(self, state):
        """
        Executes the node's logic, caracterized by a pre-processing of the HTML content and
        subsequent identification of the blocks in the HTML content.

        Args:
            state (dict): The current state of the graph. The input keys will be used
                            to fetch the correct data types from the state.

        Returns:
            dict: The updated state with a new output key containing the fetched HTML content.

        Raises:
            KeyError: If the input key is not found in the state, indicating that the
                    necessary information to perform the operation is missing.
        """
        if self.verbose:
            print(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]
