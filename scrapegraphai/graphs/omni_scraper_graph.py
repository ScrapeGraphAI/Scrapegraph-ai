"""
OmniScraperGraph Module
"""

from .base_graph import BaseGraph
from ..nodes import (
    FetchNode,
    ParseNode,
    ImageToTextNode,
    RAGNode,
    GenerateAnswerOmniNode
)
from scrapegraphai.models import OpenAIImageToText
from .abstract_graph import AbstractGraph


class OmniScraperGraph(AbstractGraph):
    """
    OmniScraper is a scraping pipeline that automates the process of 
    extracting information from web pages
    using a natural language model to interpret and answer prompts.

    Attributes:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.
        llm_model: An instance of a language model client, configured for generating answers.
        embedder_model: An instance of an embedding model client, 
        configured for generating embeddings.
        verbose (bool): A flag indicating whether to show print statements during execution.
        headless (bool): A flag indicating whether to run the graph in headless mode.

    Args:
        prompt (str): The prompt for the graph.
        source (str): The source of the graph.
        config (dict): Configuration parameters for the graph.

    Example:
        >>> omni_scraper = OmniScraperGraph(
        ...     "List me all the attractions in Chioggia and describe their pictures.",
        ...     "https://en.wikipedia.org/wiki/Chioggia",
        ...     {"llm": {"model": "gpt-4o"}}
        ... )
        >>> result = omni_scraper.run()
        )
    """

    def __init__(self, prompt: str, source: str, config: dict):

        self.max_images = 5 if config is None else config.get("max_images", 5)
        
        super().__init__(prompt, config, source)

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
        rag_node = RAGNode(
            input="user_prompt & (parsed_doc | doc)",
            output=["relevant_chunks"],
            node_config={
                "llm_model": self.llm_model,
                "embedder_model": self.embedder_model
            }
        )
        generate_answer_omni_node = GenerateAnswerOmniNode(
            input="user_prompt & (relevant_chunks | parsed_doc | doc) & img_desc",
            output=["answer"],
            node_config={
                "llm_model": self.llm_model
            }
        )

        return BaseGraph(
            nodes=[
                fetch_node,
                parse_node,
                image_to_text_node,
                rag_node,
                generate_answer_omni_node,
            ],
            edges=[
                (fetch_node, parse_node),
                (parse_node, image_to_text_node),
                (image_to_text_node, rag_node),
                (rag_node, generate_answer_omni_node)
            ],
            entry_point=fetch_node
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