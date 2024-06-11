"""
RAGNode Module
"""

from typing import List, Optional
import os

from langchain.docstore.document import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
)
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_community.vectorstores import FAISS

from ..utils.logging import get_logger
from .base_node import BaseNode


class RAGNode(BaseNode):
    """
    A node responsible for compressing the input tokens and storing the document
    in a vector database for retrieval. Relevant chunks are stored in the state.

    It allows scraping of big documents without exceeding the token limit of the language model.

    Attributes:
        llm_model: An instance of a language model client, configured for generating answers.
        embedder_model: An instance of an embedding model client, configured for generating embeddings.
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
        node_name: str = "RAG",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]
        self.embedder_model = node_config.get("embedder_model", None)
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.cache_path = node_config.get("cache_path", False)

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to implement RAG (Retrieval-Augmented Generation).
        The method updates the state with relevant chunks of the document.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data from the state.

        Returns:
            dict: The updated state with the output key containing the relevant chunks of the document.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for compressing the content is missing.
        """

        self.logger.info(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        doc = input_data[1]

        chunked_docs = []

        for i, chunk in enumerate(doc):
            doc = Document(
                page_content=chunk,
                metadata={
                    "chunk": i + 1,
                },
            )
            chunked_docs.append(doc)

        self.logger.info("--- (updated chunks metadata) ---")

        # check if embedder_model is provided, if not use llm_model
        self.embedder_model = (
            self.embedder_model if self.embedder_model else self.llm_model
        )
        embeddings = self.embedder_model

        folder_name = self.node_config.get("cache_path", "cache")

        if self.node_config.get("cache_path", False) and not os.path.exists(folder_name):
            index = FAISS.from_documents(chunked_docs, embeddings)
            os.makedirs(folder_name)
            index.save_local(folder_name)
            self.logger.info("--- (indexes saved to cache) ---")

        elif self.node_config.get("cache_path", False) and os.path.exists(folder_name):
            index = FAISS.load_local(folder_path=folder_name,
                                     embeddings=embeddings,
                                     allow_dangerous_deserialization=True)
            self.logger.info("--- (indexes loaded from cache) ---")

        else:
            index = FAISS.from_documents(chunked_docs, embeddings)

        retriever = index.as_retriever()

        redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings)
        # similarity_threshold could be set, now k=20
        relevant_filter = EmbeddingsFilter(embeddings=embeddings)
        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[redundant_filter, relevant_filter]
        )
        # redundant + relevant filter compressor
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=retriever
        )

        # relevant filter compressor only
        # compression_retriever = ContextualCompressionRetriever(
        #     base_compressor=relevant_filter, base_retriever=retriever
        # )

        compressed_docs = compression_retriever.invoke(user_prompt)

        self.logger.info("--- (tokens compressed and vector stored) ---")

        state.update({self.output[0]: compressed_docs})
        return state
