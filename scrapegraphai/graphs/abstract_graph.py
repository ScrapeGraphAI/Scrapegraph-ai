""" 
Module having abstract class for creating all the graphs
"""
from abc import ABC, abstractmethod
from typing import Optional
from ..models import OpenAI, Gemini, Ollama, AzureOpenAI
from ..helpers import models_tokens

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

        # Instantiate the language model based on the model name
        if "gpt-" in llm_params["model"]:
            try:
                self.model_token = models_tokens["openai"][llm_params["model"]]
            except KeyError:
                raise ValueError("Model not supported")
            return OpenAI(llm_params)
        
        elif "azure" in llm_params["model"]:
            # take the model after the last dash
            llm_params["model"] = llm_params["model"].split("/")[-1]
            try:
                self.model_token = models_tokens["openai"][llm_params["model"]]
            except KeyError:
                raise ValueError("Model not supported")
            return AzureOpenAI(llm_params)
        
        elif "gemini" in llm_params["model"]:
            try:
                self.model_token = models_tokens["gemini"][llm_params["model"]]
            except KeyError:
                raise ValueError("Model not supported")
            return Gemini(llm_params)
        
        elif "ollama" in llm_params["model"]:
            # take the model after the last dash
            llm_params["model"] = llm_params["model"].split("/")[-1]
            try:
                self.model_token = models_tokens["ollama"][llm_params["model"]]
            except KeyError:
                raise ValueError("Model not supported")
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
