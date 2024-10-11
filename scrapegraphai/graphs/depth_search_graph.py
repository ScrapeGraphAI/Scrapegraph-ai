"""
depth search graph Module
"""
from typing import Optional
import logging
from pydantic import BaseModel
from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from ..nodes import (
    FetchNodeLevelK,
    ParseNodeDepthK,
    DescriptionNode,
    RAGNode,
    GenerateAnswerNodeKLevel
)

class DepthSearchGraph(AbstractGraph):
    """
    CodeGeneratorGraph is a script generator pipeline that generates 
    the function extract_data(html: str) -> dict() for
    extracting the wanted information from a HTML page. The 
    code generated is in Python and uses the library BeautifulSoup.
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

        fetch_node_k = FetchNodeLevelK(
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

        parse_node_k = ParseNodeDepthK(
            input="docs",
            output=["docs"],
            node_config={
                "verbose": self.config.get("verbose", False)
            }
        )

        description_node = DescriptionNode(
            input="docs",
            output=["docs"],
            node_config={
                "llm_model": self.llm_model,
                "verbose": self.config.get("verbose", False),
                "cache_path": self.config.get("cache_path", False)
            }
        )

        rag_node = RAGNode (
            input="docs",
            output=["vectorial_db"],
            node_config={
                "llm_model": self.llm_model,
                "embedder_model": self.config.get("embedder_model", False),
                "verbose": self.config.get("verbose", False),
            }
        )

        generate_answer_k = GenerateAnswerNodeKLevel(
            input="vectorial_db",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "embedder_model": self.config.get("embedder_model", False),
                "verbose": self.config.get("verbose", False),
            }

        )

        return BaseGraph(
            nodes=[
                fetch_node_k,
                parse_node_k,
                description_node,
                rag_node,
                generate_answer_k
            ],
            edges=[
                (fetch_node_k, parse_node_k),
                (parse_node_k, description_node),
                (description_node, rag_node),
                (rag_node, generate_answer_k)
            ],
            entry_point=fetch_node_k,
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

        docs = self.final_state.get("answer", "No answer")

        return docs
