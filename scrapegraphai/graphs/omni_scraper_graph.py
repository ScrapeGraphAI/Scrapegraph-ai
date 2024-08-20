"""
OmniScraperGraph Module
"""

from typing import Optional
from pydantic import BaseModel
from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from ..nodes import (
    FetchNode,
    ParseNode,
    ImageToTextNode,
    GenerateAnswerOmniNode
)
from ..models import OpenAIImageToText

class OmniScraperGraph(AbstractGraph):
    """
    OmniScraper is a scraping pipeline that automates the process of 
    extracting information from web pages
    using a natural language model to interpret and answer prompts.

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
        max_images (int): The maximum number of images to process.

    Args:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (BaseModel): The schema for the graph output.

    Example:
        >>> omni_scraper = OmniScraperGraph(
        ...     "List me all the attractions in Chioggia and describe their pictures.",
        ...     "https://en.wikipedia.org/wiki/Chioggia",
        ...     {"llm": {"model": "gpt-4o"}}
        ... )
        >>> result = omni_scraper.run()
        )
    """

    def __init__(self, prompt: str, source: str, config: dict, schema: Optional[BaseModel] = None):

        self.max_images = 5 if config is None else config.get("max_images", 5)

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
                "loader_kwargs": self.config.get("loader_kwargs", {}),
            }
        )
        parse_node = ParseNode(
            input="doc",
            output=["parsed_doc"],
            node_config={
                "chunk_size": self.model_token
            }
        )
        image_to_text_node = ImageToTextNode(
            input="img_urls",
            output=["img_desc"],
            node_config={
                "llm_model": OpenAIImageToText(self.config["llm"]),
                "max_images": self.max_images
            }
        )

        generate_answer_omni_node = GenerateAnswerOmniNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc) & img_desc",
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
                image_to_text_node,
                generate_answer_omni_node,
            ],
            edges=[
                (fetch_node, parse_node),
                (parse_node, image_to_text_node),
                (image_to_text_node, generate_answer_omni_node)
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

        return self.final_state.get("answer", "No answer found.")
