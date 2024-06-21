"""
ScriptCreatorGraph Module
"""

from typing import Optional
from pydantic import BaseModel

from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph

from ..nodes import (
    FetchNode,
    ParseNode,
    GenerateScraperNode
)


class ScriptCreatorGraph(AbstractGraph):
    """
    ScriptCreatorGraph defines a scraping pipeline for generating web scraping scripts.

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
        model_token (int): The token limit for the language model.
        library (str): The library used for web scraping.

    Args:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel): The schema for the graph output.

    Example:
        >>> script_creator = ScriptCreatorGraph(
        ...     "List me all the attractions in Chioggia.",
        ...     "https://en.wikipedia.org/wiki/Chioggia",
        ...     {"llm": {"model": "gpt-3.5-turbo"}}
        ... )
        >>> result = script_creator.run()
    """

    def __init__(self, prompt: str, source: str, config: dict, schema: Optional[BaseModel] = None):

        self.library = config['library']

        super().__init__(prompt, config, source, schema)

        self.input_key = "url" if source.startswith("http") else "local_dir"

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: A graph instance representing the web scraping workflow.
        """

        fetch_node = FetchNode(
            input="url | local_dir",
            output=["doc", "link_urls", "img_urls"],
            node_config={
                "llm_model": self.llm_model,
                "loader_kwargs": self.config.get("loader_kwargs", {}),
                "script_creator": True
            }
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={"chunk_size": self.model_token,
                         "parse_html": False
                         }
        )
        generate_scraper_node = GenerateScraperNode(
            input="user_prompt & (doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "schema": self.schema,
            },
            library=self.library,
            website=self.source
        )

        return BaseGraph(
            nodes=[
                fetch_node,
                parse_node,
                generate_scraper_node,
            ],
            edges=[
                (fetch_node, parse_node),
                (parse_node, generate_scraper_node),
            ],
            entry_point=fetch_node,
            graph_name=self.__class__.__name__
        )

    def run(self) -> str:
        """
        Executes the web scraping process and returns the answer to the prompt.

        Returns:
            str: The answer to the prompt.
        """

        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found ")
