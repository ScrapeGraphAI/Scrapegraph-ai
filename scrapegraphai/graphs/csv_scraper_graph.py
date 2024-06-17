"""
Module for creating the smart scraper
"""

from typing import Optional
from pydantic import BaseModel

from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph

from ..nodes import (
    FetchNode,
    RAGNode,
    GenerateAnswerCSVNode
)


class CSVScraperGraph(AbstractGraph):
    """
    SmartScraper is a comprehensive web scraping tool that automates the process of extracting
    information from web pages using a natural language model to interpret and answer prompts.
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
        rag_node = RAGNode(
            input="user_prompt & doc",
            output=["relevant_chunks"],
            node_config={
                "llm_model": self.llm_model,
                "embedder_model": self.embedder_model,
            }
        )
        generate_answer_node = GenerateAnswerCSVNode(
            input="user_prompt & (relevant_chunks | doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "schema": self.schema,
            }
        )

        return BaseGraph(
            nodes=[
                fetch_node,
                rag_node,
                generate_answer_node,
            ],
            edges=[
                (fetch_node, rag_node),
                (rag_node, generate_answer_node)
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
