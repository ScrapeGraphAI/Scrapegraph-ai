"""
Module for creating the smart scraper
"""
from .base_graph import BaseGraph
from ..nodes import (
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerNodeCsv
)
from .abstract_graph import AbstractGraph


class CsvScraperGraph(AbstractGraph):
    """
    SmartScraper is a comprehensive web scraping tool that automates the process of extracting
    information from web pages using a natural language model to interpret and answer prompts.
    """

    def __init__(self, prompt: str, source: str, config: dict):
        """
        Initializes the csvScraperGraph with a prompt, source, and configuration.
        """
        super().__init__(prompt, config, source)

        self.input_key = "csv" if source.endswith("csv") else "csv_dir"

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping.
        """
        fetch_node = FetchNode(
            input="csv_dir",
            output=["doc"],
            node_config={
                "headless": self.headless,
                "verbose": self.verbose
            }
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "chunk_size": self.model_token,
                "verbose": self.verbose
            }
        )
        rag_node = RAGNode(
            input="user_prompt & (parsed_doc | doc)",
            output=["relevant_chunks"],
            node_config={
                "llm": self.llm_model,
                "embedder_model": self.embedder_model,
                "verbose": self.verbose
            }
        )
        generate_answer_node = GenerateAnswerNodeCsv(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={
                "llm": self.llm_model,
                "verbose": self.verbose
            }
        )

        return BaseGraph(
            nodes=[
                fetch_node,
                parse_node,
                rag_node,
                generate_answer_node,
            ],
            edges=[
                (fetch_node, parse_node),
                (parse_node, rag_node),
                (rag_node, generate_answer_node)
            ],
            entry_point=fetch_node
        )

    def run(self) -> str:
        """
        Executes the web scraping process and returns the answer to the prompt.
        """
        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")
