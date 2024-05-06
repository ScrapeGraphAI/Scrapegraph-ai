"""
SmartScraperGraph Module
"""

from .base_graph import BaseGraph
from ..nodes import (
    FetchNode,
    ParseNode,
    RAGNode,
    SearchLinksWithContext,
    GenerateAnswerNode
)
from .search_graph import SearchGraph
from .abstract_graph import AbstractGraph


class SmartScraperGraph(AbstractGraph):
    """
    SmartScraper is a scraping pipeline that automates the process of
    extracting information from web pages
    using a natural language model to interpret and answer prompts.

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
        >>> smart_scraper = SmartScraperGraph(
        ...     "List me all the attractions in Chioggia.",
        ...     "https://en.wikipedia.org/wiki/Chioggia",
        ...     {"llm": {"model": "gpt-3.5-turbo"}}
        ... )
        >>> result = smart_scraper.run()
        )
    """

    def __init__(self, prompt: str, source: str, config: dict):
        super().__init__(prompt, config, source)

        self.input_key = "url" if source.startswith("http") else "local_dir"

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: A graph instance representing the web scraping workflow.
        """
        fetch_node_1 = FetchNode(
            input="url | local_dir",
            output=["doc"]
        )
        parse_node_1 = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "chunk_size": self.model_token
            }
        )
        rag_node = RAGNode(
            input="user_prompt & (parsed_doc | doc)",
            output=["relevant_chunks"],
            node_config={
                "llm_model": self.llm_model,
                "embedder_model": self.embedder_model
            }
        )
        search_link_with_context_node = SearchLinksWithContext(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model
            }
        )

        search_graph = SearchGraph(
            prompt="List me the best escursions near Trento",
            config=self.llm_model
        )

        return BaseGraph(
            nodes=[
                fetch_node_1,
                parse_node_1,
                rag_node,
                search_link_with_context_node,
                search_graph
            ],
            edges=[
                (fetch_node_1, parse_node_1),
                (parse_node_1, rag_node),
                (rag_node, search_link_with_context_node),
                (search_link_with_context_node, search_graph)
            ],
            entry_point=fetch_node_1
        )

    def run(self) -> str:
        """
        Executes the scraping process and returns the answer to the prompt.

        Returns:
            str: The answer to the prompt.
        """

        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")
