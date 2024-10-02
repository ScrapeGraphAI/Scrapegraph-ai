"""
... Module
"""
from typing import Optional
import logging
from pydantic import BaseModel
from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from ..utils.save_code_to_file import save_code_to_file
from ..nodes import (
    FetchNodeLevelK
)

class DepthSearchGraph(AbstractGraph):
    """
    CodeGeneratorGraph is a script generator pipeline that generates the function extract_data(html: str) -> dict() for
    extracting the wanted information from a HTML page. The code generated is in Python and uses the library BeautifulSoup.
    It requires a user prompt, a source URL, and an output schema.

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
        library (str): The library used for web scraping (beautiful soup).

    Args:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel): The schema for the graph output.

    Example:
        >>> code_gen = CodeGeneratorGraph(
        ...     "List me all the attractions in Chioggia.",
        ...     "https://en.wikipedia.org/wiki/Chioggia",
        ...     {"llm": {"model": "openai/gpt-3.5-turbo"}}
        ... )
        >>> result = code_gen.run()
        )
    """

    def __init__(self, prompt: str, source: str, config: dict, schema: Optional[BaseModel] = None):

        super().__init__(prompt, config, source, schema)

        self.input_key = "url" if source.startswith("http") else "local_dir"

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: A graph instance representing the web scraping workflow.
        """

        fetch_node = FetchNodeLevelK(
            input="url| local_dir",
            output=["docs"],
            node_config={
                "loader_kwargs": self.config.get("loader_kwargs", {}),
                "force": self.config.get("force", False),
                "cut": self.config.get("cut", True),
                "browser_base": self.config.get("browser_base"),
                "depth": self.config.get("depth", 1),
                "only_inside_links": self.config.get("only_inside_links", False)
            }
        )

        return BaseGraph(
            nodes=[
                fetch_node
            ],
            edges=[],
            entry_point=fetch_node,
            graph_name=self.__class__.__name__
        )

    def run(self) -> str:
        """
        Executes the scraping process and returns the generated code.

        Returns:
            str: The generated code.
        """

        inputs = {"user_prompt": self.prompt, self.input_key: self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        docs = self.final_state.get("docs", "No docs")

        return docs