"""
SearchGraph Module
"""

from copy import deepcopy
from typing import Optional, List
from pydantic import BaseModel
from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from .smart_scraper_graph import SmartScraperGraph
from ..nodes import SearchInternetNode, GraphIteratorNode, MergeAnswersNode
from ..utils.copy import safe_deepcopy


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
        considered_urls (List[str]): A list of URLs considered during the search.

    Args:
        prompt (str): The user prompt to search the internet.
        config (dict): Configuration parameters for the graph.
        schema (Optional[BaseModel]): The schema for the graph output.

    Example:
        >>> search_graph = SearchGraph(
        ...     "What is Chioggia famous for?",
        ...     {"llm": {"model": "openai/gpt-3.5-turbo"}}
        ... )
        >>> result = search_graph.run()
        >>> print(search_graph.get_considered_urls())
    """

    def __init__(self, prompt: str, config: dict, schema: Optional[BaseModel] = None):
        self.max_results = config.get("max_results", 3)

        self.copy_config = safe_deepcopy(config)
        self.copy_schema = deepcopy(schema)
        self.considered_urls = []  # New attribute to store URLs

        super().__init__(prompt, config, schema)

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping and searching.

        Returns:
            BaseGraph: A graph instance representing the web scraping and searching workflow.
        """

        search_internet_node = SearchInternetNode(
            input="user_prompt",
            output=["urls"],
            node_config={
                "llm_model": self.llm_model,
                "max_results": self.max_results,
                "loader_kwargs": self.loader_kwargs,
                "storage_state": self.copy_config.get("storage_state"),
                "search_engine": self.copy_config.get("search_engine"),
                "serper_api_key": self.copy_config.get("serper_api_key"),
            },
        )

        graph_iterator_node = GraphIteratorNode(
            input="user_prompt & urls",
            output=["results"],
            node_config={
                "graph_instance": SmartScraperGraph,
                "scraper_config": self.copy_config,
            },
            schema=self.copy_schema,
        )

        merge_answers_node = MergeAnswersNode(
            input="user_prompt & results",
            output=["answer"],
            node_config={"llm_model": self.llm_model, "schema": self.copy_schema},
        )

        return BaseGraph(
            nodes=[search_internet_node, graph_iterator_node, merge_answers_node],
            edges=[
                (search_internet_node, graph_iterator_node),
                (graph_iterator_node, merge_answers_node),
            ],
            entry_point=search_internet_node,
            graph_name=self.__class__.__name__,
        )

    def run(self) -> str:
        """
        Executes the web scraping and searching process.

        Returns:
            str: The answer to the prompt.
        """

        inputs = {"user_prompt": self.prompt}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        # Store the URLs after execution
        if "urls" in self.final_state:
            self.considered_urls = self.final_state["urls"]

        return self.final_state.get("answer", "No answer found.")

    def get_considered_urls(self) -> List[str]:
        """
        Returns the list of URLs considered during the search.

        Returns:
            List[str]: A list of URLs considered during the search.
        """

        return self.considered_urls
