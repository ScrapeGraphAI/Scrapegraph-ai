"""
AbstractGraph Module
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..models import OpenAI, Gemini, Ollama, AzureOpenAI, HuggingFace, Groq, Bedrock
from ..helpers import models_tokens


class AbstractGraph(ABC):
    """
    Scaffolding class for creating a graph representation and executing it.

    Attributes:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        llm_model: An instance of a language model client, configured for generating answers.
        embedder_model: An instance of an embedding model client, configured for generating embeddings.
        verbose (bool): A flag indicating whether to show print statements during execution.
        headless (bool): A flag indicating whether to run the graph in headless mode.

    Args:
        prompt (str): The prompt for the graph.
        config (dict): Configuration parameters for the graph.
        source (str, optional): The source of the graph.

    Example:
        >>> class MyGraph(AbstractGraph):
        ...     def _create_graph(self):
        ...         # Implementation of graph creation here
        ...         return graph
        ...
        >>> my_graph = MyGraph("Example Graph", {"llm": {"model": "gpt-3.5-turbo"}}, "example_source")
        >>> result = my_graph.run()
    """

    def __init__(self, prompt: str, config: dict, source: Optional[str] = None):

        self.prompt = prompt
        self.source = source
        self.config = config
        self.llm_model = self._create_llm(config["llm"], chat=True)
        self.embedder_model = self.llm_model if "embeddings" not in config else self._create_llm(
            config["embeddings"])

        # Set common configuration parameters
        self.verbose = True if config is None else config.get("verbose", False)
        self.headless = True if config is None else config.get(
            "headless", True)

        # Create the graph
        self.graph = self._create_graph()
        self.final_state = None
        self.execution_info = None


    def _set_model_token(self, llm):

        if 'Azure' in str(type(llm)):
            try:
                self.model_token = models_tokens["azure"][llm.model_name]
            except KeyError:
                raise KeyError("Model not supported")


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

        llm_defaults = {
            "temperature": 0,
            "streaming": False
        }
        llm_params = {**llm_defaults, **llm_config}

        # If model instance is passed directly instead of the model details
        if 'model_instance' in llm_params:
            if chat:
                self._set_model_token(llm_params['model_instance'])
            return llm_params['model_instance']
        
        # Instantiate the language model based on the model name
        if "gpt-" in llm_params["model"]:
            try:
                self.model_token = models_tokens["openai"][llm_params["model"]]
            except KeyError:
                raise KeyError("Model not supported")
            return OpenAI(llm_params)

        elif "azure" in llm_params["model"]:
            # take the model after the last dash
            llm_params["model"] = llm_params["model"].split("/")[-1]
            try:
                self.model_token = models_tokens["azure"][llm_params["model"]]
            except KeyError:
                raise KeyError("Model not supported")
            return AzureOpenAI(llm_params)

        elif "gemini" in llm_params["model"]:
            try:
                self.model_token = models_tokens["gemini"][llm_params["model"]]
            except KeyError:
                raise KeyError("Model not supported")
            return Gemini(llm_params)

        elif "ollama" in llm_params["model"]:
            llm_params["model"] = llm_params["model"].split("/")[-1]

            # allow user to set model_tokens in config
            try:
                if "model_tokens" in llm_params:
                    self.model_token = llm_params["model_tokens"]
                elif llm_params["model"] in models_tokens["ollama"]:
                    try:
                        self.model_token = models_tokens["ollama"][llm_params["model"]]
                    except KeyError:
                        raise KeyError("Model not supported")
                else:
                    self.model_token = 8192
            except AttributeError:
                self.model_token = 8192

            return Ollama(llm_params)
        elif "hugging_face" in llm_params["model"]:
            try:
                self.model_token = models_tokens["hugging_face"][llm_params["model"]]
            except KeyError:
                raise KeyError("Model not supported")
            return HuggingFace(llm_params)
        elif "groq" in llm_params["model"]:
            llm_params["model"] = llm_params["model"].split("/")[-1]

            try:
                self.model_token = models_tokens["groq"][llm_params["model"]]
            except KeyError:
                raise KeyError("Model not supported")
            return Groq(llm_params)
        elif "bedrock" in llm_params["model"]:
            llm_params["model"] = llm_params["model"].split("/")[-1]
            model_id = llm_params["model"]

            try:
                self.model_token = models_tokens["bedrock"][llm_params["model"]]
            except KeyError:
                raise KeyError("Model not supported")
            return Bedrock({
                "model_id": model_id,
                "model_kwargs": {
                    "temperature": llm_params["temperature"],
                }
            })
        else:
            raise ValueError(
                "Model provided by the configuration not supported")

    def get_state(self, key=None) -> dict:
        """""
        Get the final state of the graph.

        Args:
            key (str, optional): The key of the final state to retrieve.

        Returns:
            dict: The final state of the graph.
        """

        if key is not None:
            return self.final_state[key]
        return self.final_state

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

