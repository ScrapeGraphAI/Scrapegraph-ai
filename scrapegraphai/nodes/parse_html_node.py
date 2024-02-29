"""
Module for parsing the HTML node
"""
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers import Html2TextTransformer
from .base_node import BaseNode


class ParseHTMLNode(BaseNode):
    """
    A node responsible for parsing HTML content from a document using specified tags. 
    It uses BeautifulSoupTransformer for parsing, providing flexibility in extracting
    specific parts of an HTML document based on the tags provided in the state.

    This node enhances the scraping workflow by allowing for targeted extraction of 
    content, thereby optimizing the processing of large HTML documents.

    Attributes:
        node_name (str): The unique identifier name for the node, defaulting to "ParseHTMLNode".
        node_type (str): The type of the node, set to "node" indicating a standard operational node.

    Args:
        node_name (str, optional): The unique identifier name for the node. 
        Defaults to "ParseHTMLNode".

    Methods:
        execute(state): Parses the HTML document contained within the state using 
        the specified tags, if provided, and updates the state with the parsed content.
    """

    def __init__(self, node_name: str):
        """
        Initializes the ParseHTMLNode with a node name.
        Args:
            node_name (str): name of the node
            node_type (str, optional): type of the node
        """
        super().__init__(node_name, "node")

    def execute(self,  state):
        """
        Executes the node's logic to parse the HTML document based on specified tags. 
        If tags are provided in the state, the document is parsed accordingly; otherwise, 
        the document remains unchanged. The method updates the state with either the original 
        or parsed document under the 'parsed_document' key.

        Args:
            state (dict): The current state of the graph, expected to contain 
            'document' within 'keys', and optionally 'tags' for targeted parsing.

        Returns:
            dict: The updated state with the 'parsed_document' key containing the parsed content,
                  if tags were provided, or the original document otherwise.

        Raises:
            KeyError: If 'document' is not found in the state, indicating that the necessary 
                      information for parsing is missing.
        """

        print("---PARSING HTML DOCUMENT---")
        try:
            document = state["document"]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=4000,
            chunk_overlap=0,
        )

        docs_transformed = Html2TextTransformer(
        ).transform_documents(document)[0]

        chunks = text_splitter.split_text(docs_transformed.page_content)

        state.update({"document_chunks": chunks})

        return state
