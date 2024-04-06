""" 
Module having abstract class for creating all the graphs
"""
from abc import ABC, abstractmethod
from typing import Optional

class AbstractGraph(ABC):
    """
    Abstract class representing a generic graph-based tool.
    """

    def __init__(self, prompt: str, config: dict, file_source: Optional[str] = "url"):
        """
        Initializes the AbstractGraph with a prompt, file source, and configuration.
        """
        self.prompt = prompt
        self.file_source = file_source
        self.input_key = "url" if file_source.startswith(
            "http") else "local_dir"
        self.config = config
        self.llm_model = self._create_llm(config["llm"])
        self.graph = self._create_graph()

    @abstractmethod
    def _create_llm(self, llm_config: dict):
        """
        Abstract method to create a language model instance.
        """
        pass

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
