"""
Module for parsing the HTML node
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_transformers import Html2TextTransformer
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain_community.document_transformers import EmbeddingsRedundantFilter

from .base_node import BaseNode


class RAGNode(BaseNode):
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

    def __init__(self, llm, node_name="TestRagNode"):
        """
        Initializes the ParseHTMLNode with a node name.
        """
        super().__init__(node_name, "node")
        self.llm = llm

    def execute(self, state):
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

        print("---PARSE HTML DOCUMENT---")
        try:
            user_input = state["user_input"]
            document = state["document"]
        except KeyError as e:
            print(f"Error: {e} not found in state.")
            raise

        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=4000,
            chunk_overlap=0,
        )

        docs_transformed = Html2TextTransformer().transform_documents(document)[0]

        chunks = text_splitter.split_text(docs_transformed.page_content)
        chunked_docs = []

        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "chunk": i + 1,
                },
            )
            chunked_docs.append(doc)
        
        openai_key = self.llm.openai_api_key
        retriever = FAISS.from_documents(chunked_docs, OpenAIEmbeddings(api_key=openai_key)).as_retriever()
        embeddings = OpenAIEmbeddings(api_key=openai_key) # could be any embedding of your choice
        redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings)
        relevant_filter = EmbeddingsFilter(embeddings=embeddings) # similarity_threshold could be set, now k=20
        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[redundant_filter, relevant_filter]
        )

        compression_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=retriever
        )

        compressed_docs = compression_retriever.get_relevant_documents(user_input)
        print("Documents compressed and stored in a vector database.")
        state.update({"relevant_chunks": compressed_docs})
        return state
