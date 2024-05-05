"""
JSONScraperGraph Module
"""

from .base_graph import BaseGraph
from ..nodes import (
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerNode
)
from .abstract_graph import AbstractGraph


class JSONScraperGraph(AbstractGraph):
    """
    JSONScraperGraph defines a scraping pipeline for JSON files.

    Attributes:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        llm_model: An instance of a language model client, configured for generating answers.
        embedder_model: An instance of an embedding model client, 
        configured for generating embeddings.
        verbose (bool): A flag indicating whether to show print statements during execution.
        headless (bool): A flag indicating whether to run the graph in headless mode.

    Args:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.

    Example:
        >>> json_scraper = JSONScraperGraph(
        ...     "List me all the attractions in Chioggia.",
        ...     "data/chioggia.json",
        ...     {"llm": {"model": "gpt-3.5-turbo"}}
        ... )
        >>> result = json_scraper.run()
    """

    def __init__(self, prompt: str, source: str, config: dict):
        super().__init__(prompt, config, source)

        self.input_key = "json" if source.endswith("json") else "json_dir"

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: A graph instance representing the web scraping workflow.
        """

        fetch_node = FetchNode(
            input="json_dir",
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
                "llm_model": self.llm_model,
                "embedder_model": self.embedder_model,
                "verbose": self.verbose
            }
        )
        generate_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
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

        Returns:
            str: The answer to the prompt.
        """

        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")
