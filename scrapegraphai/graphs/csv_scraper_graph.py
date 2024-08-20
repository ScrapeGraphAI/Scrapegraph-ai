"""
Module for creating the smart scraper
"""

from typing import Optional
from pydantic import BaseModel
from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from ..nodes import (
    FetchNode,
    GenerateAnswerCSVNode
)

class CSVScraperGraph(AbstractGraph):
    """
    A class representing a graph for extracting information from CSV files.

    Attributes:
        prompt (str): The prompt used to generate an answer.
        source (str): The source of the data, which can be either a CSV 
        file or a directory containing multiple CSV files.
        config (dict): Additional configuration parameters needed by some nodes in the graph.

    Methods:
        __init__ (prompt: str, source: str, config: dict, schema: Optional[BaseModel] = None):
            Initializes the CSVScraperGraph with a prompt, source, and configuration.

        __init__ initializes the CSVScraperGraph class. It requires the user's prompt as input, 
            along with the source of the data (which can be either a single CSV file or a directory 
            containing multiple CSV files), and any necessary configuration parameters.

    Methods:
        _create_graph (): Creates the graph of nodes representing the workflow for web scraping.

        _create_graph generates the web scraping process workflow 
            represented by a directed acyclic graph. 
            This method is used internally to create the scraping pipeline 
            without having to execute it immediately. The result is a BaseGraph instance 
            containing nodes that fetch and process data from a source, and other helper functions.

    Methods:
        run () -> str: Executes the web scraping process and returns 
            the answer to the prompt as a string.
        run runs the CSVScraperGraph class to extract information from a CSV file based 
            on the user's prompt. It requires no additional arguments since all necessary data 
            is stored within the class instance. The method fetches the relevant chunks of text or speech,
            generates an answer based on these chunks, and returns this answer as a string.
    """

    def __init__(self, prompt: str, source: str, config: dict, schema: Optional[BaseModel] = None):
        """
        Initializes the CSVScraperGraph with a prompt, source, and configuration.
        """
        super().__init__(prompt, config, source, schema)

        self.input_key = "csv" if source.endswith("csv") else "csv_dir"

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping.
        """
        fetch_node = FetchNode(
            input="csv | csv_dir",
            output=["doc"],
        )

        generate_answer_node = GenerateAnswerCSVNode(
            input="user_prompt & (relevant_chunks | doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "additional_info": self.config.get("additional_info"),
                "schema": self.schema,
            }
        )

        return BaseGraph(
            nodes=[
                fetch_node,
                generate_answer_node,
            ],
            edges=[
                (fetch_node, generate_answer_node)
            ],
            entry_point=fetch_node,
            graph_name=self.__class__.__name__
        )

    def run(self) -> str:
        """
        Executes the web scraping process and returns the answer to the prompt.
        """
        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")
