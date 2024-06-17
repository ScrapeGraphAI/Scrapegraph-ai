""" 
ScriptCreatorMultiGraph Module
"""

from copy import copy, deepcopy
from typing import List, Optional

from .base_graph import BaseGraph
from .abstract_graph import AbstractGraph
from .script_creator_graph import ScriptCreatorGraph

from ..nodes import (
    GraphIteratorNode,
    MergeGeneratedScriptsNode
)


class ScriptCreatorMultiGraph(AbstractGraph):
    """ 
    ScriptCreatorMultiGraph is a scraping pipeline that scrapes a list of URLs generating web scraping scripts.
    It only requires a user prompt and a list of URLs.
    Attributes:
        prompt (str): The user prompt to search the internet.
        llm_model (dict): The configuration for the language model.
        embedder_model (dict): The configuration for the embedder model.
        headless (bool): A flag to run the browser in headless mode.
        verbose (bool): A flag to display the execution information.
        model_token (int): The token limit for the language model.
    Args:
        prompt (str): The user prompt to search the internet.
        source (List[str]): The source of the graph.
        config (dict): Configuration parameters for the graph.
        schema (Optional[str]): The schema for the graph output.
    Example:
        >>> script_graph = ScriptCreatorMultiGraph(
        ...     "What is Chioggia famous for?",
        ...     source=[],
        ...     config={"llm": {"model": "gpt-3.5-turbo"}}
        ...     schema={}
        ... )
        >>> result = script_graph.run()
    """

    def __init__(self, prompt: str, source: List[str], config: dict, schema: Optional[str] = None):

        self.max_results = config.get("max_results", 3)

        if all(isinstance(value, str) for value in config.values()):
            self.copy_config = copy(config)
        else:
            self.copy_config = deepcopy(config)

        super().__init__(prompt, config, source, schema)

    def _create_graph(self) -> BaseGraph:
        """
        Creates the graph of nodes representing the workflow for web scraping and searching.
        Returns:
            BaseGraph: A graph instance representing the web scraping and searching workflow.
        """

        # ************************************************
        # Create a ScriptCreatorGraph instance
        # ************************************************

        script_generator_instance = ScriptCreatorGraph(
            prompt="",
            source="",
            config=self.copy_config,
            schema=self.schema
        )

        # ************************************************
        # Define the graph nodes
        # ************************************************

        graph_iterator_node = GraphIteratorNode(
            input="user_prompt & urls",
            output=["scripts"],
            node_config={
                "graph_instance": script_generator_instance,
            }
        )

        merge_scripts_node = MergeGeneratedScriptsNode(
            input="user_prompt & scripts",
            output=["merged_script"],
            node_config={
                "llm_model": self.llm_model,
                "schema": self.schema
            }
        )

        return BaseGraph(
            nodes=[
                graph_iterator_node,
                merge_scripts_node,
            ],
            edges=[
                (graph_iterator_node, merge_scripts_node),
            ],
            entry_point=graph_iterator_node,
            graph_name=self.__class__.__name__
        )

    def run(self) -> str:
        """
        Executes the web scraping and searching process.
        Returns:
            str: The answer to the prompt.
        """
        inputs = {"user_prompt": self.prompt, "urls": self.source}
        self.final_state, self.execution_info = self.graph.execute(inputs)
        return self.final_state.get("merged_script", "Failed to generate the script.")