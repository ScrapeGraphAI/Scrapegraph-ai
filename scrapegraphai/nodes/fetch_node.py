""" 
FetchNode Module
"""

from typing import List, Optional
from langchain_community.document_loaders import AsyncChromiumLoader
from langchain_core.documents import Document
from .base_node import BaseNode
from ..utils.remover import remover


class FetchNode(BaseNode):
    """
    A node responsible for fetching the HTML content of a specified URL and updating
    the graph's state with this content. It uses the AsyncChromiumLoader to fetch the
    content asynchronously.

    This node acts as a starting point in many scraping workflows, preparing the state
    with the necessary HTML content for further processing by subsequent nodes in the graph.

    Attributes:
        headless (bool): A flag indicating whether the browser should run in headless mode.
        verbose (bool): A flag indicating whether to print verbose output during execution.
    
    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (Optional[dict]): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Fetch".
    """

    def __init__(self, input: str, output: List[str], node_config: Optional[dict]=None, node_name: str = "Fetch"):
        super().__init__(node_name, "node", input, output, 1)

        self.headless = True if node_config is None else node_config.get("headless", True)
        self.verbose = False if node_config is None else node_config.get("verbose", False)

    def execute(self, state):
        """
        Executes the node's logic to fetch HTML content from a specified URL and
        update the state with this content.

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

        source = input_data[0]
        if self.input == "json_dir" or self.input == "xml_dir" or self.input == "csv_dir":
            compressed_document = [Document(page_content=source, metadata={
                "source": "local_dir"
            })]
        # if it is a local directory
        elif not source.startswith("http"):
            compressed_document = [Document(page_content=remover(source), metadata={
                "source": "local_dir"
            })]

        else:
            if self.node_config is not None and self.node_config.get("endpoint") is not None:
                
                loader = AsyncChromiumLoader(
                    [source],
                    proxies={"http": self.node_config["endpoint"]},
                    headless=self.headless,
                )
            else:
                loader = AsyncChromiumLoader(
                    [source],
                    headless=self.headless,
                )

            document = loader.load()
            compressed_document = [
                Document(page_content=remover(str(document[0].page_content)))]

        state.update({self.output[0]: compressed_document})
        return state
