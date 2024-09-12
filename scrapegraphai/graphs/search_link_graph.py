""" 
SearchLinkGraph Module 
"""
from typing import Optional
import logging
from pydantic import BaseModel
from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from ..nodes import ( FetchNode, ParseNode, SearchLinkNode )

class SearchLinkGraph(AbstractGraph): 
    """ 
    SearchLinkGraph is a scraping pipeline that automates the process of 
    extracting information from web pages using a natural language model
    to interpret and answer prompts.

    Attributes:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel): The schema for the graph output.
        llm_model: An instance of a language model client, configured for generating answers.
        embedder_model: An instance of an embedding model client, 
        configured for generating embeddings.
        verbose (bool): A flag indicating whether to show print statements during execution.
        headless (bool): A flag indicating whether to run the graph in headless mode.

    Args:
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel, optional): The schema for the graph output. Defaults to None.

    Example:
        >>> smart_scraper = SearchLinkGraph(
        ...     "List me all the attractions in Chioggia.",
        ...     "https://en.wikipedia.org/wiki/Chioggia",
        ...     {"llm": {"model": "openai/gpt-3.5-turbo"}}
        ... )
        >>> result = smart_scraper.run()
    """

    def __init__(self, source: str, config: dict, schema: Optional[BaseModel] = None):
        super().__init__("", config, source, schema)

        self.input_key = "url" if source.startswith("http") else "local_dir"

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: A graph instance representing the web scraping workflow.
        """

        fetch_node = FetchNode(
            input="url| local_dir",
            output=["doc"],
            node_config={
                "llm_model": self.llm_model,
                "force": self.config.get("force", False),
                "cut": self.config.get("cut", True),
                "loader_kwargs": self.config.get("loader_kwargs", {}),
            }
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "chunk_size": self.model_token,
                "llm_model": self.llm_model
            }
        )
        search_link_node = SearchLinkNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "llm_model": self.llm_model,
                "chunk_size": self.model_token,
                "filter_links": self.config.get("filter_links", None),
                "filter_config": self.config.get("filter_config", None)
            }
        )

        return BaseGraph(
            nodes=[
                fetch_node,
                parse_node,
                search_link_node
            ],
            edges=[
                (fetch_node, parse_node),
                (parse_node, search_link_node)
            ],
            entry_point=fetch_node,
            graph_name=self.__class__.__name__
        )

    def run(self) -> str:
        """
        Executes the scraping process and returns the answer to the prompt.

        Returns:
            str: The answer to the prompt.
        """

        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("parsed_doc", "No answer found.")
