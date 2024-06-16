"""
AbstractGraph Module
"""

from abc import ABC, abstractmethod
from typing import Optional, Union
import uuid
from pydantic import BaseModel

from langchain_aws import BedrockEmbeddings
from langchain_community.embeddings import HuggingFaceHubEmbeddings, OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings

from ..helpers import models_tokens
from ..models import (
    Anthropic,
    AzureOpenAI,
    Bedrock,
    Gemini,
    Groq,
    HuggingFace,
    Ollama,
    OpenAI,
    OneApi
)
from ..models.ernie import Ernie
from ..utils.logging import set_verbosity_debug, set_verbosity_warning

from ..helpers import models_tokens
from ..models import AzureOpenAI, Bedrock, Gemini, Groq, HuggingFace, Ollama, OpenAI, Anthropic, DeepSeek


class AbstractGraph(ABC):
    """
    Scaffolding class for creating a graph representation and executing it.

        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (str): The schema for the graph output.
        llm_model: An instance of a language model client, configured for generating answers.
        embedder_model: An instance of an embedding model client,
                        configured for generating embeddings.
        verbose (bool): A flag indicating whether to show print statements during execution.
        headless (bool): A flag indicating whether to run the graph in headless mode.

    Args:
        prompt (str): The prompt for the graph.
        config (dict): Configuration parameters for the graph.
        source (str, optional): The source of the graph.
        schema (str, optional): The schema for the graph output.

    Example:
        >>> class MyGraph(AbstractGraph):
        ...     def _create_graph(self):
        ...         # Implementation of graph creation here
        ...         return graph
        ...
        >>> my_graph = MyGraph("Example Graph", 
        {"llm": {"model": "gpt-3.5-turbo"}}, "example_source")
        >>> result = my_graph.run()
    """

    def __init__(self, prompt: str, config: dict, 
                 source: Optional[str] = None, schema: Optional[BaseModel] = None):

        self.prompt = prompt
        self.source = source
        self.config = config
        self.schema = schema
        self.llm_model = self._create_llm(config["llm"], chat=True)
        self.embedder_model = self._create_default_embedder(llm_config=config["llm"]                                                            ) if "embeddings" not in config else self._create_embedder(
            config["embeddings"])
        self.verbose = False if config is None else config.get(
            "verbose", False)
        self.headless = True if config is None else config.get(
            "headless", True)
        self.loader_kwargs = config.get("loader_kwargs", {})
        self.cache_path = config.get("cache_path", False)

        # Create the graph
        self.graph = self._create_graph()
        self.final_state = None
        self.execution_info = None

        # Set common configuration parameters

        verbose = bool(config and config.get("verbose"))

        if verbose:
            set_verbosity_debug()
        else:
            set_verbosity_warning()

        common_params = {
            "headless": self.headless,
            "verbose": self.verbose,
            "loader_kwargs": self.loader_kwargs,
            "llm_model": self.llm_model,
            "embedder_model": self.embedder_model,
            "cache_path": self.cache_path,
            }
       
        self.set_common_params(common_params, overwrite=True)

        # set burr config
        self.burr_kwargs = config.get("burr_kwargs", None)
        if self.burr_kwargs is not None:
            self.graph.use_burr = True
            if "app_instance_id" not in self.burr_kwargs:
                # set a random uuid for the app_instance_id to avoid conflicts
                self.burr_kwargs["app_instance_id"] = str(uuid.uuid4())

            self.graph.burr_config = self.burr_kwargs

    def set_common_params(self, params: dict, overwrite=False):
        """
        Pass parameters to every node in the graph unless otherwise defined in the graph.

        Args:
            params (dict): Common parameters and their values.
        """

        for node in self.graph.nodes:
            node.update_config(params, overwrite)
    
    def _create_llm(self, llm_config: dict, chat=False) -> object:
        """
        Create a large language model instance based on the configuration provided.

        Args:
            llm_config (dict): Configuration parameters for the language model.

        Returns:
            object: An instance of the language model client.

        Raises:
            KeyError: If the model is not supported.
        """

        llm_defaults = {"temperature": 0, "streaming": False}
        llm_params = {**llm_defaults, **llm_config}

        # If model instance is passed directly instead of the model details
        if "model_instance" in llm_params:
            return llm_params["model_instance"]

        # Instantiate the language model based on the model name
        if "gpt-" in llm_params["model"]:
            try:
                self.model_token = models_tokens["openai"][llm_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return OpenAI(llm_params)
        elif "oneapi" in llm_params["model"]:
            # take the model after the last dash
            llm_params["model"] = llm_params["model"].split("/")[-1]
            try:
                self.model_token = models_tokens["oneapi"][llm_params["model"]]
            except KeyError as exc:
                raise KeyError("Model Model not supported") from exc
            return OneApi(llm_params)
        elif "azure" in llm_params["model"]:
            # take the model after the last dash
            llm_params["model"] = llm_params["model"].split("/")[-1]
            try:
                self.model_token = models_tokens["azure"][llm_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return AzureOpenAI(llm_params)

        elif "gemini" in llm_params["model"]:
            try:
                self.model_token = models_tokens["gemini"][llm_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return Gemini(llm_params)
        elif llm_params["model"].startswith("claude"):
            try:
                self.model_token = models_tokens["claude"][llm_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return Anthropic(llm_params)
        elif "ollama" in llm_params["model"]:
            llm_params["model"] = llm_params["model"].split("ollama/")[-1]

            # allow user to set model_tokens in config
            try:
                if "model_tokens" in llm_params:
                    self.model_token = llm_params["model_tokens"]
                elif llm_params["model"] in models_tokens["ollama"]:
                    try:
                        self.model_token = models_tokens["ollama"][llm_params["model"]]
                    except KeyError as exc:
                        print("model not found, using default token size (8192)")
                        self.model_token = 8192
                else:
                    self.model_token = 8192
            except AttributeError:
                self.model_token = 8192

            return Ollama(llm_params)
        elif "hugging_face" in llm_params["model"]:
            try:
                self.model_token = models_tokens["hugging_face"][llm_params["model"]]
            except KeyError:
                print("model not found, using default token size (8192)")
                self.model_token = 8192
            return HuggingFace(llm_params)
        elif "groq" in llm_params["model"]:
            llm_params["model"] = llm_params["model"].split("/")[-1]

            try:
                self.model_token = models_tokens["groq"][llm_params["model"]]
            except KeyError:
                print("model not found, using default token size (8192)")
                self.model_token = 8192
            return Groq(llm_params)
        elif "bedrock" in llm_params["model"]:
            llm_params["model"] = llm_params["model"].split("/")[-1]
            model_id = llm_params["model"]
            client = llm_params.get("client", None)
            try:
                self.model_token = models_tokens["bedrock"][llm_params["model"]]
            except KeyError:
                print("model not found, using default token size (8192)")
                self.model_token = 8192
            return Bedrock(
                {
                    "client": client,
                    "model_id": model_id,
                    "model_kwargs": {
                        "temperature": llm_params["temperature"],
                    },
                }
            )
        elif "claude-3-" in llm_params["model"]:
            try:
                self.model_token = models_tokens["claude"]["claude3"]
            except KeyError:
                print("model not found, using default token size (8192)")
                self.model_token = 8192
            return Anthropic(llm_params)
        elif "deepseek" in llm_params["model"]:
            try:
                self.model_token = models_tokens["deepseek"][llm_params["model"]]
            except KeyError:
                print("model not found, using default token size (8192)")
                self.model_token = 8192
            return DeepSeek(llm_params)
        elif "ernie" in llm_params["model"]:
            try:
                self.model_token = models_tokens["ernie"][llm_params["model"]]
            except KeyError:
                print("model not found, using default token size (8192)")
                self.model_token = 8192
            return Ernie(llm_params)
        else:
            raise ValueError("Model provided by the configuration not supported")

    def _create_default_embedder(self, llm_config=None) -> object:
        """
        Create an embedding model instance based on the chosen llm model.

        Returns:
            object: An instance of the embedding model client.

        Raises:
            ValueError: If the model is not supported.
        """
        if isinstance(self.llm_model, Gemini):
            return GoogleGenerativeAIEmbeddings(
                google_api_key=llm_config["api_key"], model="models/embedding-001"
            )
        if isinstance(self.llm_model, OpenAI):
            return OpenAIEmbeddings(api_key=self.llm_model.openai_api_key)
        elif isinstance(self.llm_model, AzureOpenAIEmbeddings):
            return self.llm_model
        elif isinstance(self.llm_model, AzureOpenAI):
            return AzureOpenAIEmbeddings()
        elif isinstance(self.llm_model, Ollama):
            # unwrap the kwargs from the model whihc is a dict
            params = self.llm_model._lc_kwargs
            # remove streaming and temperature
            params.pop("streaming", None)
            params.pop("temperature", None)

            return OllamaEmbeddings(**params)
        elif isinstance(self.llm_model, HuggingFace):
            return HuggingFaceHubEmbeddings(model=self.llm_model.model)
        elif isinstance(self.llm_model, Bedrock):
            return BedrockEmbeddings(client=None, model_id=self.llm_model.model_id)
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
        # Instantiate the embedding model based on the model name
        if "openai" in embedder_params["model"]:
            return OpenAIEmbeddings(api_key=embedder_params["api_key"])
        elif "azure" in embedder_params["model"]:
            return AzureOpenAIEmbeddings()
        elif "ollama" in embedder_params["model"]:
            embedder_params["model"] = embedder_params["model"].split("ollama/")[-1]
            try:
                models_tokens["ollama"][embedder_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return OllamaEmbeddings(**embedder_params)
        elif "hugging_face" in embedder_params["model"]:
            try:
                models_tokens["hugging_face"][embedder_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return HuggingFaceHubEmbeddings(model=embedder_params["model"])
        elif "gemini" in embedder_params["model"]:
            try:
                models_tokens["gemini"][embedder_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return GoogleGenerativeAIEmbeddings(model=embedder_params["model"])
        elif "bedrock" in embedder_params["model"]:
            embedder_params["model"] = embedder_params["model"].split("/")[-1]
            client = embedder_params.get("client", None)
            try:
                models_tokens["bedrock"][embedder_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return BedrockEmbeddings(client=client, model_id=embedder_params["model"])
        else:
            raise ValueError("Model provided by the configuration not supported")

    def get_state(self, key=None) -> dict:
        """ ""
        Get the final state of the graph.

        Args:
            key (str, optional): The key of the final state to retrieve.

        Returns:
            dict: The final state of the graph.
        """

        if key is not None:
            return self.final_state[key]
        return self.final_state

    def append_node(self, node):
        """
        Add a node to the graph.

        Args:
            node (BaseNode): The node to add to the graph.
        """

        self.graph.append_node(node)

    def get_execution_info(self):
        """
        Returns the execution information of the graph.

        Returns:
            dict: The execution information of the graph.
        """

        return self.execution_info

    @abstractmethod
    def _create_graph(self):
        """
        Abstract method to create a graph representation.
        """
        pass

    @abstractmethod
    def run(self) -> str:
        """
        Abstract method to execute the graph and return the result.
        """
        pass