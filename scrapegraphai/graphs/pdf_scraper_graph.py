
"""
PDFScraperGraph Module
"""

from typing import Optional
from pydantic import BaseModel

from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph

from ..nodes import (
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerPDFNode
)


class PDFScraperGraph(AbstractGraph):
    """
    PDFScraperGraph is a scraping pipeline that extracts information from pdf files using a natural
    language model to interpret and answer prompts.

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

    Args:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel): The schema for the graph output.

    Example:
        >>> pdf_scraper = PDFScraperGraph(
        ...     "List me all the attractions in Chioggia.",
        ...     "data/chioggia.pdf",
        ...     {"llm": {"model": "gpt-3.5-turbo"}}
        ... )
        >>> result = pdf_scraper.run()
    """

    def __init__(self, prompt: str, source: str, config: dict, schema: Optional[BaseModel] = None):
        super().__init__(prompt, config, source, schema)

        self.input_key = "pdf" if source.endswith("pdf") else "pdf_dir"

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping.

        Returns:
            BaseGraph: A graph instance representing the web scraping workflow.
        """

        fetch_node = FetchNode(
            input='pdf | pdf_dir',
            output=["doc"],
        )

        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "parse_html": False,
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
        generate_answer_node_pdf = GenerateAnswerPDFNode(
            input="user_prompt & (relevant_chunks | doc)",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model,
                "additional_info": self.config.get("additional_info"),
                "schema": self.schema
            }
        )

        return BaseGraph(
            nodes=[
                fetch_node,
                parse_node,
                rag_node,
                generate_answer_node_pdf,
            ],
            edges=[
                (fetch_node, parse_node),
                (parse_node, rag_node),
                (rag_node, generate_answer_node_pdf)
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

        return self.final_state.get("answer", "No answer found.")
