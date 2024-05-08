""" 
SearchGraph Module
"""

from copy import deepcopy

from .base_graph import BaseGraph
from ..nodes import (
    SearchInternetNode,
    GraphIteratorNode,
    MergeAnswersNode
)
from .abstract_graph import AbstractGraph
from .smart_scraper_graph import SmartScraperGraph


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

    def __init__(self, prompt: str, config: dict):

        self.max_results = config.get("max_results", 3)
        self.copy_config = deepcopy(config)

        super().__init__(prompt, config)

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping and searching.

        Returns:
            BaseGraph: A graph instance representing the web scraping and searching workflow.
        """

        # ************************************************
        # Create a SmartScraperGraph instance
        # ************************************************

        smart_scraper_instance = SmartScraperGraph(
            prompt="",
            source="",
            config=self.copy_config
        )

        # ************************************************
        # Define the graph nodes
        # ************************************************

        search_internet_node = SearchInternetNode(
            input="user_prompt",
            output=["urls"],
            node_config={
                "llm_model": self.llm_model,
                "max_results": self.max_results
            }
        )
        graph_iterator_node = GraphIteratorNode(
            input="user_prompt & urls",
            output=["results"],
            node_config={
                "graph_instance": smart_scraper_instance,
            }
        )

        merge_answers_node = MergeAnswersNode(
            input="user_prompt & results",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
            }
        )

        return BaseGraph(
            nodes=[
                search_internet_node,
                graph_iterator_node,
                merge_answers_node
            ],
            edges=[
                (search_internet_node, graph_iterator_node),
                (graph_iterator_node, merge_answers_node)
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
