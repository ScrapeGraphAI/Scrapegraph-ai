""" 
ScreenshotScraperGraph Module 
"""
from typing import Optional
import logging
from pydantic import BaseModel
from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from ..nodes import ( FetchScreenNode, GenerateAnswerFromImageNode, )

class ScreenshotScraperGraph(AbstractGraph): 
    """ 
    A graph instance representing the web scraping workflow for images.

    Attributes:
        prompt (str): The input text to be scraped.
        config (dict): Configuration parameters for the graph.
        source (str): The source URL or image link to scrape from.

    Methods:
        __init__(prompt: str, source: str, config: dict, schema: Optional[BaseModel] = None)
            Initializes the ScreenshotScraperGraph instance with the given prompt, 
            source, and configuration parameters.

        _create_graph()
            Creates a graph of nodes representing the web scraping workflow for images.

        run()
            Executes the scraping process and returns the answer to the prompt.
    """

    def __init__(self, prompt: str, source: str, config: dict, schema: Optional[BaseModel] = None):
        super().__init__(prompt, config, source, schema)


    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping with images.

        Returns:
            BaseGraph: A graph instance representing the web scraping workflow for images.
        """
        fetch_screen_node = FetchScreenNode(
            input="url",
            output=["screenshots"],
            node_config={
                "link": self.source
            }
        )
        generate_answer_from_image_node = GenerateAnswerFromImageNode(
            input="screenshots",
            output=["answer"],
            node_config={
                "config": self.config
            }
        )

        return BaseGraph(
            nodes=[
                fetch_screen_node,
                generate_answer_from_image_node,
            ],
            edges=[
                (fetch_screen_node, generate_answer_from_image_node),
            ],
            entry_point=fetch_screen_node,
            graph_name=self.__class__.__name__
        )

    def run(self) -> str:
        """
        Executes the scraping process and returns the answer to the prompt.

        Returns:
            str: The answer to the prompt.
        """

        inputs = {"user_prompt": self.prompt}
        self.final_state, self.execution_info = self.graph.execute(inputs)

        return self.final_state.get("answer", "No answer found.")
        