""" 
OmniSearchGraph Module
"""

from copy import copy, deepcopy
from typing import Optional
from pydantic import BaseModel

from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from .omni_scraper_graph import OmniScraperGraph

from ..nodes import (
    SearchInternetNode,
    GraphIteratorNode,
    MergeAnswersNode
)


class OmniSearchGraph(AbstractGraph):
    """ 
    OmniSearchGraph is a scraping pipeline that searches the internet for answers to a given prompt.
    It only requires a user prompt to search the internet and generate an answer.

    Attributes:
        prompt (str): The user prompt to search the internet.
        llm_model (dict): The configuration for the language model.
        embedder_model (dict): The configuration for the embedder model.
        headless (bool): A flag to run the browser in headless mode.
        verbose (bool): A flag to display the execution information.
        model_token (int): The token limit for the language model.
        max_results (int): The maximum number of results to return.

    Args:
        prompt (str): The user prompt to search the internet.
        config (dict): Configuration parameters for the graph.
        schema (Optional[str]): The schema for the graph output.

    Example:
        >>> omni_search_graph = OmniSearchGraph(
        ...     "What is Chioggia famous for?",
        ...     {"llm": {"model": "gpt-4o"}}
        ... )
        >>> result = search_graph.run()
    """

    def __init__(self, prompt: str, config: dict, schema: Optional[BaseModel] = None):

        self.max_results = config.get("max_results", 3)

        if all(isinstance(value, str) for value in config.values()):
            self.copy_config = copy(config)
        else:
            self.copy_config = deepcopy(config)

        self.copy_schema = deepcopy(schema)

        super().__init__(prompt, config, schema)

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping and searching.

        Returns:
            BaseGraph: A graph instance representing the web scraping and searching workflow.
        """

        # ************************************************
        # Create a OmniScraperGraph instance
        # ************************************************

        omni_scraper_instance = OmniScraperGraph(
            prompt="",
            source="",
            config=self.copy_config,
            schema=self.copy_schema
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
                "graph_instance": omni_scraper_instance,
            }
        )

        merge_answers_node = MergeAnswersNode(
            input="user_prompt & results",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "schema": self.schema
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
            entry_point=search_internet_node,
            graph_name=self.__class__.__name__
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
