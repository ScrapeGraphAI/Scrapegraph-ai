"""
IndexifyNode Module
"""

from typing import List, Optional

from ..utils.logging import get_logger
from ..nodes.base_node import BaseNode

# try:
#     import indexify
# except ImportError:
#     raise ImportError("indexify package is not installed. Please install it with 'pip install scrapegraphai[indexify]'")


class IndexifyNode(BaseNode):
    """
    A node responsible for indexing the content present in the state.

    Attributes:
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Parse".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "Indexify",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to index the content present in the state.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data from the state.

        Returns:
            dict: The updated state with the output key containing the parsed content chunks.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for parsing the content is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        # input_keys length matches the min_input_len parameter in the __init__ method
        # e.g. "answer & parsed_doc" or "answer | img_urls"
        
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        answer = input_data[0]
        img_urls = input_data[1]

        # Indexify the content
        # ...

        isIndexified = True
        state.update({self.output[0]: isIndexified})

        return state
