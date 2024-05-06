""" 
SearchGraph Module
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
    SearchGraph is a scraping pipeline that searches the internet for answers to a given prompt.
    It only requires a user prompt to search the internet and generate an answer.

    Attributes:
        prompt (str): The user prompt to search the internet.
        llm_model (dict): The configuration for the language model.
        embedder_model (dict): The configuration for the embedder model.
        headless (bool): A flag to run the browser in headless mode.
        verbose (bool): A flag to display the execution information.
        model_token (int): The token limit for the language model.

    Args:
        prompt (str): The user prompt to search the internet.
        config (dict): Configuration parameters for the graph.

    Example:
        >>> search_graph = SearchGraph(
        ...     "What is Chioggia famous for?",
        ...     {"llm": {"model": "gpt-3.5-turbo"}}
        ... )
        >>> result = search_graph.run()
    """

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping and searching.

        Returns:
            BaseGraph: A graph instance representing the web scraping and searching workflow.
        """

        search_internet_node = SearchInternetNode(
            input="user_prompt",
            output=["url"],
            node_config={
                "llm_model": self.llm_model
            }
        )
        fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc"]
        )
        parse_node = ParseNode(
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
        generate_answer_node = GenerateAnswerNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model
            }
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

        Returns:
            str: The answer to the prompt.
        """
        inputs = {"user_prompt": self.prompt}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")
