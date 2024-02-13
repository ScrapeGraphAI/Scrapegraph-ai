from langchain_community.document_loaders import AsyncHtmlLoader
from .base_node import BaseNode

class FetchHTMLNode(BaseNode):
    def __init__(self, node_name, node_type="node"):
        super().__init__(node_name, node_type)

    def execute(self, state):
        """
        Fetches HTML document for the given URL and updates the state with the document.

        Args:
            state (dict): The current state of the graph, expected to contain a 'url' key.

        Returns:
            dict: The updated state with a new 'document' key containing the HTML content.
        """
        try:
            url = state["keys"]["url"]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise
        loader = AsyncHtmlLoader(url)
        document = loader.load()
        state["keys"]["document"] = document

        return state
