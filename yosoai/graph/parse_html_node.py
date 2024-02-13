from .base_node import BaseNode
from langchain_community.document_transformers import BeautifulSoupTransformer

class ParseHTMLNode(BaseNode):
    def __init__(self, node_name="ParseHTMLNode"):
        super().__init__(node_name, "node")

    def execute(self, state):
        """
        Checks for the 'tags' key in the state. If it exists, parses the document
        based on these tags. Otherwise, returns the document as is.
        
        Args:
            state (dict): The current state of the graph, expected to contain
                          'document' within 'keys', and optionally 'tags'.
        
        Returns:
            dict: The updated state with 'parsed_document' within 'keys',
                  containing either the original or parsed document.
        """
        
        print("---PARSE HTML DOCUMENT---")
        try:
            document = state["keys"]["document"]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise

        # Check if tags are specified in the state
        tags = state["keys"].get("tags", None)

        if tags:
            # Initialize the BeautifulSoupTransformer with any required configurations
            bs_transformer = BeautifulSoupTransformer()
            # Parse the document with specified tags
            parsed_document = bs_transformer.transform_documents(document, tags_to_extract=tags)
            print("Document parsed with specified tags.")
        else:
            # If no tags are specified, return the document as is
            print("No specific tags provided; returning document as is.")
            return state

        # Update the state with the parsed document
        state["keys"].update({"parsed_document": parsed_document})
        return state