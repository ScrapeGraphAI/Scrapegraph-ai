""" 
Module for fetching the HTML node
"""
from langchain_community.document_loaders import AsyncHtmlLoader
from .base_node import BaseNode

from ..utils.remover import remover


class FetchHTMLNode(BaseNode):
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

    def __init__(self, node_name: str):
        """
        Initializes the FetchHTMLNode with a node name and node type.
        Arguments:
            node_name (str): name of the node
        """
        super().__init__(node_name, "node")

    def execute(self, state: dict) -> dict:
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
        print("---FETCHING HTML CODE---")
        try:
            url = state["url"]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise

        loader = AsyncHtmlLoader(url)
        document = loader.load()

        document = remover(document, only_body=True)

        state["document"] = document

        return state
