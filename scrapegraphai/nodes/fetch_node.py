""" 
Module for fetching the HTML node
"""

from typing import List
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_core.documents import Document
from .base_node import BaseNode
from ..utils.remover import remover


class FetchNode(BaseNode):
    """
    A node responsible for fetching the HTML content of a specified URL and updating
    the graph's state with this content. It uses the AsyncHtmlLoader for asynchronous
    document loading.

    This node acts as a starting point in many scraping workflows, preparing the state
    with the necessary HTML content for further processing by subsequent nodes in the graph.

    Attributes:
        node_name (str): The unique identifier name for the node.
        node_type (str): The type of the node, defaulting to "node". This categorization
                         helps in determining the node's role and behavior within the graph.
                         The "node" type is used for standard operational nodes.

    Args:
        node_name (str): The unique identifier name for the node. This name is used to
                         reference the node within the graph.
        node_type (str, optional): The type of the node, limited to "node" or
                                   "conditional_node". Defaults to "node".

    Methods:
        execute(state): Fetches the HTML content for the URL specified in the state and
                        updates the state with this content under the 'document' key.
                        The 'url' key must be present in the state for the operation
                        to succeed.
    """

    def __init__(self, input: str, output: List[str], node_name: str = "Fetch"):
        """
        Initializes the FetchHTMLNode with a node name and node type.
        Arguments:
            node_name (str): name of the node
            prox_rotation (bool): if you wamt to rotate proxies
        """
        super().__init__(node_name, "node", input, output, 1)

    def execute(self, state):
        """
        Executes the node's logic to fetch HTML content from a specified URL and
        update the state with this content.

        Args:
            state (dict): The current state of the graph, expected to contain a 'url' key.

        Returns:
            dict: The updated state with a new 'document' key containing the fetched HTML content.

        Raises:
            KeyError: If the 'url' key is not found in the state, indicating that the
                    necessary information to perform the operation is missing.
        """
        print(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        source = input_data[0]
        if self.input == "json_dir" or self.input == "xml_dir":
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
                loader = AsyncHtmlLoader(
                    source, proxies={"http": self.node_config["endpoint"]})
            else:
                loader = AsyncHtmlLoader(source)

            document = loader.load()
            compressed_document = [
                Document(page_content=remover(str(document)))]

        state.update({self.output[0]: compressed_document})
        return state
