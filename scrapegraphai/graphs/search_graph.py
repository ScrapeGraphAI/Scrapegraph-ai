""" 
Module for making the search on the intenet
"""
from .base_graph import BaseGraph
from ..nodes import (
    SearchInternetNode,
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerNode
)
from .abstract_graph import AbstractGraph


class SearchGraph(AbstractGraph):
    """ 
    Module for searching info on the internet
    """

    def _create_graph(self):
        """
        Creates the graph of nodes representing the workflow for web scraping and searching.
        """
        search_internet_node = SearchInternetNode(
            input="user_prompt",
            output=["url"],
            node_config={"llm": self.llm_model}
        )
        fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc"],
            node_config={"headless": True if self.config is None else self.config.get("headless", True)}
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
            nodes=[
                search_internet_node,
                fetch_node,
                parse_node,
                rag_node,
                generate_answer_node,
            ],
            edges=[
                (search_internet_node, fetch_node),
                (fetch_node, parse_node),
                (parse_node, rag_node),
                (rag_node, generate_answer_node)
            ],
            entry_point=search_internet_node
        )

    def run(self) -> str:
        """
        Executes the web scraping and searching process.
        """
        inputs = {"user_prompt": self.prompt}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")
