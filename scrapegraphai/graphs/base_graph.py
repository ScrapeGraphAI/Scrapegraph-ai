"""
Module for creating the base graphs
 """
import time
from langchain_community.callbacks import get_openai_callback


class BaseGraph:
    """
    BaseGraph manages the execution flow of a graph composed of interconnected nodes.

    Attributes:
        nodes (dict): A dictionary mapping each node's name to its corresponding node instance.
        edges (dict): A dictionary representing the directed edges of the graph where each 
                      key-value pair corresponds to the from-node and to-node relationship.
        entry_point (str): The name of the entry point node from which the graph execution begins.

    Methods:
        execute(initial_state): Executes the graph's nodes starting from the entry point and 
                                traverses the graph based on the provided initial state.

    Args:
        nodes (iterable): An iterable of node instances that will be part of the graph.
        edges (iterable): An iterable of tuples where each tuple represents a directed edge 
                          in the graph, defined by a pair of nodes (from_node, to_node).
        entry_point (BaseNode): The node instance that represents the entry point of the graph.
    """

    def __init__(self, nodes: dict, edges: dict, entry_point: str):
        """
        Initializes the graph with nodes, edges, and the entry point.
        """
        self.nodes = {node.node_name: node for node in nodes}
        self.edges = self._create_edges(edges)
        self.entry_point = entry_point.node_name

    def _create_edges(self, edges: dict) -> dict:
        """
        Helper method to create a dictionary of edges from the given iterable of tuples.

        Args:
            edges (iterable): An iterable of tuples representing the directed edges.

        Returns:
            dict: A dictionary of edges with the from-node as keys and to-node as values.
        """
        edge_dict = {}
        for from_node, to_node in edges:
            edge_dict[from_node.node_name] = to_node.node_name
        return edge_dict

    def execute(self, initial_state: dict) -> dict:
        """
        Executes the graph by traversing nodes starting from the entry point. The execution 
        follows the edges based on the result of each node's execution and continues until 
        it reaches a node with no outgoing edges.

        Args:
            initial_state (dict): The initial state to pass to the entry point node.

        Returns:
            dict: The state after execution has completed, which may have been altered by the nodes.
        """
        current_node_name = self.entry_point
        state = initial_state

        # variables for tracking execution info
        total_exec_time = 0.0
        exec_info = {}
        cb_total = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": 0,
            "total_cost_USD": 0.0,
        }

        while current_node_name is not None:

            curr_time = time.time()
            current_node = self.nodes[current_node_name]

            with get_openai_callback() as cb:
                result = current_node.execute(state)
                node_exec_time = time.time() - curr_time
                total_exec_time += node_exec_time

                cb = {
                    "total_tokens": cb.total_tokens,
                    "prompt_tokens": cb.prompt_tokens,
                    "completion_tokens": cb.completion_tokens,
                    "successful_requests": cb.successful_requests,
                    "total_cost_USD": cb.total_cost,
                }

                exec_info[current_node_name] = {
                    "exec_time": node_exec_time,
                    "model_info": cb
                }

                cb_total["total_tokens"] += cb["total_tokens"]
                cb_total["prompt_tokens"] += cb["prompt_tokens"]
                cb_total["completion_tokens"] += cb["completion_tokens"]
                cb_total["successful_requests"] += cb["successful_requests"]
                cb_total["total_cost_USD"] += cb["total_cost_USD"]

            if current_node.node_type == "conditional_node":
                current_node_name = result
            elif current_node_name in self.edges:
                current_node_name = self.edges[current_node_name]
            else:
                current_node_name = None

        execution_info = {
            "total_exec_time": total_exec_time,
            "total_model_info": cb_total,
            "nodes_info": exec_info
        }

        return state, execution_info
