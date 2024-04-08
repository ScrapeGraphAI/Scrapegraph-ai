""" 
Module having abstract class for creating all the graphs
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..models import OpenAI, Gemini, Ollama, AzureOpenAI

class AbstractGraph(ABC):
    """
    Abstract class representing a generic graph-based tool.
    """

    def __init__(self, prompt: str, config: dict, source: Optional[str] = None):
        """
        Initializes the AbstractGraph with a prompt, file source, and configuration.
        """
        self.prompt = prompt
        self.source = source
        self.input_key = "url" if source.startswith(
            "http") else "local_dir"
        self.config = config
        self.llm_model = self._create_llm(config["llm"])
        self.embedder_model = None if "embeddings" not in config else self._create_llm(config["embeddings"])
        self.graph = self._create_graph()

    def _create_llm(self, llm_config: dict):
        """
        Creates an instance of the language model (OpenAI or Gemini) based on configuration.
        """
        llm_defaults = {
            "temperature": 0,
            "streaming": True
        }
        llm_params = {**llm_defaults, **llm_config}

        if "gpt-" in llm_params["model"]:
            return OpenAI(llm_params)
        elif "azure" in llm_params["model"]:
            return AzureOpenAI(llm_params)
        elif "gemini" in llm_params["model"]:
            return Gemini(llm_params)
        elif "llama2" in llm_params["model"]:
            # set model to llama2 if it has a different structure
            llm_params["model"] = "llama2"
            return Ollama(llm_params)
        else:
            raise ValueError("Model not supported")

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
