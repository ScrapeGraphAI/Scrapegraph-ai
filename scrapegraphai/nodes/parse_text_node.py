"""
Module for parsing the HTML node
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .base_node import BaseNode


class ParseTextNode(BaseNode):
    """
    A node for extracting content from HTML documents based on provided tags.

    This node leverages the BeautifulSoupTransformer to offer flexible parsing 
    capabilities. It allows you to isolate specific elements within an HTML 
    document, making it valuable for targeted content extraction in scraping workflows.

    Attributes:
        node_name (str): Unique name for the node (defaults to "ParseHTMLNode").
        node_type (str): Indicates a standard operational node (set to "node").

    Args:
        node_name (str, optional): Custom name for the node (defaults to "ParseHTMLNode").

    Methods:
        execute(state):  
            * Extracts content from the 'document' field in the state based on tags (if provided in the state).
            * Stores the result in the 'parsed_document' field of the state.
            * Employs the RecursiveCharacterTextSplitter for handling larger documents.
    """

    def __init__(self, node_name: str = "ParseHTMLNode"):
        """
        Initializes the ParseHTMLNode.

        Args:
            node_name (str, optional): Custom name for the node (defaults to "ParseHTMLNode").
        """
        super().__init__(node_name, "node")

    def execute(self, state):
        """
        Parses HTML content and updates the state.

        Args:
            state (dict):  Expects the following keys:
                'document': The HTML content to parse.
                'tags' (optional): A list of HTML tags to target for extraction.

        Returns:
            dict: Updated state with the following:
                'parsed_document': The extracted content 
                (or the original document if no tags were provided).
                'document_chunks': The original document split into chunka
                 (using RecursiveCharacterTextSplitter) 
                for larger documents.

        Raises:
            KeyError: If the required 'document' key is missing from the state.
        """

        print("---PARSING TEXT DOCUMENT---")

        try:
            document = state["document"]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise

        # ... (Add logic for parsing with BeautifulSoup based on 'tags' if present)

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=4000,
            chunk_overlap=0,
        )
        state["document_chunks"] = text_splitter.split_text(document)

        return state
