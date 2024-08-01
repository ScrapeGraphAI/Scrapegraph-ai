"""
AbstractGraph Module
"""

from abc import ABC, abstractmethod
from typing import Optional
import uuid
from pydantic import BaseModel

from langchain_community.chat_models import ErnieBotChat
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.chat_models import init_chat_model

from ..helpers import models_tokens
from ..models import (
    OneApi,
    DeepSeek
)
from ..utils.logging import set_verbosity_warning, set_verbosity_info



class AbstractGraph(ABC):
    """
    Scaffolding class for creating a graph representation and executing it.

        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel): The schema for the graph output.
        llm_model: An instance of a language model client, configured for generating answers.
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
        self.llm_model = self._create_llm(config["llm"])
        self.verbose = False if config is None else config.get(
            "verbose", False)
        self.headless = True if self.config is None else config.get(
            "headless", True)
        self.loader_kwargs = self.config.get("loader_kwargs", {})
        self.cache_path = self.config.get("cache_path", False)
        self.browser_base = self.config.get("browser_base")

        # Create the graph
        self.graph = self._create_graph()
        self.final_state = None
        self.execution_info = None

        # Set common configuration parameters

        verbose = bool(config and config.get("verbose"))

        if verbose:
            set_verbosity_info()
        else:
            set_verbosity_warning()

        common_params = {
            "headless": self.headless,
            "verbose": self.verbose,
            "loader_kwargs": self.loader_kwargs,
            "llm_model": self.llm_model,
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

    def _create_llm(self, llm_config: dict) -> object:
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
            try:
                self.model_token = llm_params["model_tokens"]
            except KeyError as exc:
                raise KeyError("model_tokens not specified") from exc
            return llm_params["model_instance"]

        # Instantiate the language model based on the model name (models that use the common interface)
        def handle_model(model_name, provider, token_key, default_token=8192):
            try:
                self.model_token = models_tokens[provider][token_key]
            except KeyError:
                print(f"Model not found, using default token size ({default_token})")
                self.model_token = default_token
            llm_params["model_provider"] = provider
            llm_params["model"] = model_name
            return init_chat_model(**llm_params)

        if "gpt-" in llm_params["model"]:
            return handle_model(llm_params["model"], "openai", llm_params["model"])

        if "fireworks" in llm_params["model"]:
            model_name = "/".join(llm_params["model"].split("/")[1:])
            token_key = llm_params["model"].split("/")[-1]
            return handle_model(model_name, "fireworks", token_key)

        if "azure" in llm_params["model"]:
            model_name = llm_params["model"].split("/")[-1]
            return handle_model(model_name, "azure_openai", model_name)

        if "gemini" in llm_params["model"]:
            model_name = llm_params["model"].split("/")[-1]
            return handle_model(model_name, "google_genai", model_name)

        if llm_params["model"].startswith("claude"):
            model_name = llm_params["model"].split("/")[-1]
            return handle_model(model_name, "anthropic", model_name)

        if llm_params["model"].startswith("vertexai"):
            return handle_model(llm_params["model"], "google_vertexai", llm_params["model"])

        if "ollama" in llm_params["model"]:
            model_name = llm_params["model"].split("ollama/")[-1]
            token_key = model_name if "model_tokens" not in llm_params else llm_params["model_tokens"]
            return handle_model(model_name, "ollama", token_key)

        if "hugging_face" in llm_params["model"]:
            model_name = llm_params["model"].split("/")[-1]
            return handle_model(model_name, "hugging_face", model_name)

        if "groq" in llm_params["model"]:
            model_name = llm_params["model"].split("/")[-1]
            return handle_model(model_name, "groq", model_name)

        if "bedrock" in llm_params["model"]:
            model_name = llm_params["model"].split("/")[-1]
            return handle_model(model_name, "bedrock", model_name)

        if "claude-3-" in llm_params["model"]:
            return handle_model(llm_params["model"], "anthropic", "claude3")

        # Instantiate the language model based on the model name (models that do not use the common interface)
        if "deepseek" in llm_params["model"]:
            try:
                self.model_token = models_tokens["deepseek"][llm_params["model"]]
            except KeyError:
                print("model not found, using default token size (8192)")
                self.model_token = 8192
            return DeepSeek(llm_params)

        if "ernie" in llm_params["model"]:
            try:
                self.model_token = models_tokens["ernie"][llm_params["model"]]
            except KeyError:
                print("model not found, using default token size (8192)")
                self.model_token = 8192
            return ErnieBotChat(llm_params)
        
        if "oneapi" in llm_params["model"]:
            # take the model after the last dash
            llm_params["model"] = llm_params["model"].split("/")[-1]
            try:
                self.model_token = models_tokens["oneapi"][llm_params["model"]]
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return OneApi(llm_params)
        
        if "nvidia" in llm_params["model"]:
            try:
                self.model_token = models_tokens["nvidia"][llm_params["model"].split("/")[-1]]
                llm_params["model"] = "/".join(llm_params["model"].split("/")[1:])
            except KeyError as exc:
                raise KeyError("Model not supported") from exc
            return ChatNVIDIA(llm_params)

        # Raise an error if the model did not match any of the previous cases
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

    @abstractmethod
    def run(self) -> str:
        """
        Abstract method to execute the graph and return the result.
        """
