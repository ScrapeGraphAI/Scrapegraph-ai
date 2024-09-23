"""
RAGNode Module
"""
import os
import sys
from typing import List, Optional
from langchain.docstore.document import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
)
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_aws import BedrockEmbeddings, ChatBedrock
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings, ChatOpenAI, AzureChatOpenAI
from ..utils.logging import get_logger
from .base_node import BaseNode
from ..helpers import models_tokens
from ..models import DeepSeek

optional_modules = {"langchain_anthropic", "langchain_fireworks",
                    "langchain_groq", "langchain_google_vertexai"}

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
        # Execution logic
        pass

    def _create_default_embedder(self, llm_config=None) -> object:
        """
        Create an embedding model instance based on the chosen llm model.

        Returns:
            object: An instance of the embedding model client.

        Raises:
            ValueError: If the model is not supported.
        """

        if isinstance(self.llm_model, ChatGoogleGenerativeAI):
            return GoogleGenerativeAIEmbeddings(
                google_api_key=llm_config["api_key"], model="models/embedding-001"
            )
        if isinstance(self.llm_model, ChatOpenAI):
            return OpenAIEmbeddings(api_key=self.llm_model.openai_api_key,
                                    base_url=self.llm_model.openai_api_base)
        elif isinstance(self.llm_model, DeepSeek):
            return OpenAIEmbeddings(api_key=self.llm_model.openai_api_key)
        elif isinstance(self.llm_model, AzureOpenAIEmbeddings):
            return self.llm_model
        elif isinstance(self.llm_model, AzureChatOpenAI):
            return AzureOpenAIEmbeddings()
        elif isinstance(self.llm_model, ChatOllama):
            params = self.llm_model._lc_kwargs
            params.pop("streaming", None)
            params.pop("temperature", None)
            return OllamaEmbeddings(**params)
        elif isinstance(self.llm_model, ChatBedrock):
            return BedrockEmbeddings(client=None, model_id=self.llm_model.model_id)
        elif all(key in sys.modules for key in optional_modules):
            if isinstance(self.llm_model, ChatFireworks):
                from langchain_fireworks import FireworksEmbeddings
                return FireworksEmbeddings(model=self.llm_model.model_name)
            if isinstance(self.llm_model, ChatNVIDIA):
                from langchain_nvidia import NVIDIAEmbeddings
                return NVIDIAEmbeddings(model=self.llm_model.model_name)
            if isinstance(self.llm_model, ChatHuggingFace):
                from langchain_huggingface import HuggingFaceEmbeddings
                return HuggingFaceEmbeddings(model=self.llm_model.model)
            if isinstance(self.llm_model, ChatVertexAI):
                from langchain_vertexai import VertexAIEmbeddings
                return VertexAIEmbeddings()
        else:
            raise ValueError("Embedding Model missing or not supported")

    def _create_embedder(self, embedder_config: dict) -> object:
        """
        Create an embedding model instance based on the configuration provided.

        Args:
            embedder_config (dict): Configuration parameters for the embedding model.

        Returns:
            object: An instance of the embedding model client.

        Raises:
            KeyError: If the model is not supported.
        """
        embedder_params = {**embedder_config}
        if "model_instance" in embedder_config:
            return embedder_params["model_instance"]
        if "openai" in embedder_params["model"]:
            return OpenAIEmbeddings(api_key=embedder_params["api_key"])
        if "azure" in embedder_params["model"]:
            return AzureOpenAIEmbeddings()
        if "ollama" in embedder_params["model"]:
            embedder_params["model"] = "/".join(embedder_params["model"].split("/")[1:])
            try:
                models_tokens["ollama"][embedder_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return OllamaEmbeddings(**embedder_params)
        if "gemini" in embedder_params["model"]:
            try:
                models_tokens["gemini"][embedder_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return GoogleGenerativeAIEmbeddings(model=embedder_params["model"])
        if "bedrock" in embedder_params["model"]:
            embedder_params["model"] = embedder_params["model"].split("/")[-1]
            client = embedder_params.get("client", None)
            try:
                models_tokens["bedrock"][embedder_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return BedrockEmbeddings(client=client, model_id=embedder_params["model"])
        if all(key in sys.modules for key in optional_modules):
            if "hugging_face" in embedder_params["model"]:
                from langchain_huggingface import HuggingFaceEmbeddings
                embedder_params["model"] = "/".join(embedder_params["model"].split("/")[1:])
                try:
                    models_tokens["hugging_face"][embedder_params["model"]]
                except KeyError as exc:
                    raise KeyError("Model not supported") from exc
                return HuggingFaceEmbeddings(model=embedder_params["model"])
            elif "fireworks" in embedder_params["model"]:
                from langchain_fireworks import FireworksEmbeddings
                embedder_params["model"] = "/".join(embedder_params["model"].split("/")[1:])
                try:
                    models_tokens["fireworks"][embedder_params["model"]]
                except KeyError as exc:
                    raise KeyError("Model not supported") from exc
                return FireworksEmbeddings(model=embedder_params["model"])
            elif "nvidia" in embedder_params["model"]:
                from langchain_nvidia import NVIDIAEmbeddings
                embedder_params["model"] = "/".join(embedder_params["model"].split("/")[1:])
                try:
                    models_tokens["nvidia"][embedder_params["model"]]
                except KeyError as exc:
                    raise KeyError("Model not supported") from exc
                return NVIDIAEmbeddings(model=embedder_params["model"],
                                        nvidia_api_key=embedder_params["api_key"])

        raise ValueError("Model provided by the configuration not supported")
