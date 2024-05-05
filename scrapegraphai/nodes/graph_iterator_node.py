"""
GraphIterator Module
"""

from typing import List, Optional
import copy
from tqdm import tqdm
from .base_node import BaseNode


class GraphIteratorNode(BaseNode):
    """
    A node responsible for parsing HTML content from a document. 
    The parsed content is split into chunks for further processing.

    This node enhances the scraping workflow by allowing for targeted extraction of 
    content, thereby optimizing the processing of large HTML documents.

    Attributes:
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Parse".
    """

    def __init__(self, input: str, output: List[str], node_config: Optional[dict]=None, node_name: str = "GraphIterator"):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.verbose = False if node_config is None else node_config.get("verbose", False)

    def execute(self,  state: dict) -> dict:
        """
        Executes the node's logic to parse the HTML document content and split it into chunks.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch the
                            correct data from the state.

        Returns:
            dict: The updated state with the output key containing the parsed content chunks.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for parsing the content is missing.
        """

        if self.verbose:
            print(f"--- Executing {self.node_name} Node ---")

        # Interpret input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # Fetching data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        urls = input_data[1]

        graph_instance = self.node_config.get("graph_instance", None)
        if graph_instance is None:
            raise ValueError("Graph instance is required for graph iteration.")
        
        # set the prompt and source for each url
        graph_instance.prompt = user_prompt
        graphs_instances = []
        for url in urls:
            # make a copy of the graph instance
            copy_graph_instance = copy.copy(graph_instance)
            copy_graph_instance.source = url
            graphs_instances.append(copy_graph_instance)

        # run the graph for each url and use tqdm for progress bar
        graphs_answers = []
        for graph in tqdm(graphs_instances, desc="Processing Graph Instances", disable=not self.verbose):
            result = graph.run()
            graphs_answers.append(result)

        state.update({self.output[0]: graphs_answers})

        return state
