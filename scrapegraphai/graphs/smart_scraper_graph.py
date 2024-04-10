""" 
Module for creating the smart scraper
"""
from .base_graph import BaseGraph
from ..nodes import (
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerNode
)
from .abstract_graph import AbstractGraph


class SmartScraperGraph(AbstractGraph):
    """
    SmartScraper is a comprehensive web scraping tool that automates the process of extracting
    information from web pages using a natural language model to interpret and answer prompts.
    """

    def __init__(self, prompt: str, source: str, config: dict):
        """
        Initializes the SmartScraperGraph with a prompt, source, and configuration.
        """
        super().__init__(prompt, config, source)

        self.input_key = "url" if source.startswith("http") else "local_dir"

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping.
        """
        fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc"],
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={"chunk_size": self.model_token}
        )
        rag_node = RAGNode(
            input="user_prompt & (parsed_doc | doc)",
            output=["relevant_chunks"],
            node_config={
                "llm": self.llm_model,
                "embedder_model": self.embedder_model
            }
        )
        generate_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={"llm": self.llm_model},
        )

        return BaseGraph(
            nodes={
                fetch_node,
                parse_node,
                rag_node,
                generate_answer_node,
            },
            edges={
                (fetch_node, parse_node),
                (parse_node, rag_node),
                (rag_node, generate_answer_node)
            },
            entry_point=fetch_node
        )

    def run(self) -> str:
        """
        Executes the web scraping process and returns the answer to the prompt.
        """
        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        final_state = self.graph.execute(inputs)

        return final_state.get("answer", "No answer found.")
