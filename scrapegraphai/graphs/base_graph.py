"""
BaseGraph Module
"""

import time
import warnings
from langchain_community.callbacks import get_openai_callback
from typing import Tuple
from collections import deque


class BaseGraph:
    """
    BaseGraph manages the execution flow of a graph composed of interconnected nodes.

    Attributes:
        nodes (list): A dictionary mapping each node's name to its corresponding node instance.
        edges (list): A dictionary representing the directed edges of the graph where each
                      key-value pair corresponds to the from-node and to-node relationship.
        entry_point (str): The name of the entry point node from which the graph execution begins.

    Args:
        nodes (iterable): An iterable of node instances that will be part of the graph.
        edges (iterable): An iterable of tuples where each tuple represents a directed edge
                          in the graph, defined by a pair of nodes (from_node, to_node).
        entry_point (BaseNode): The node instance that represents the entry point of the graph.

    Raises:
        Warning: If the entry point node is not the first node in the list.
        ValueError: If conditional_node does not have exactly two outgoing edges


    Example:
        >>> BaseGraph(
        ...    nodes=[
        ...        fetch_node,
        ...        parse_node,
        ...        rag_node,
        ...        generate_answer_node,
        ...    ],
        ...    edges=[
        ...        (fetch_node, parse_node),
        ...        (parse_node, rag_node),
        ...        (rag_node, generate_answer_node)
        ...    ],
        ...    entry_point=fetch_node
        ... )
    """

    def __init__(self, nodes: list, edges: list, entry_point: str):

        self.nodes = nodes
        self.edges = self._create_edges({e for e in edges})
        self.entry_point = entry_point

        if nodes[0].node_name != entry_point.node_name:
            # raise a warning if the entry point is not the first node in the list
            warnings.warn(
                "Careful! The entry point node is different from the first node if the graph.")

    def _create_edges(self, edges: list) -> dict:
        """
        Helper method to create a dictionary of edges from the given iterable of tuples.

        Args:
            edges (iterable): An iterable of tuples representing the directed edges.

        Returns:
            dict: A dictionary of edges with the from-node as keys and to-node as values.
        """

        edge_dict = {}
        for from_node, to_node in edges:
            if from_node in edge_dict:
                edge_dict[from_node].append(to_node)
            else:
                edge_dict[from_node] = [to_node]
        return edge_dict

    def execute(self, initial_state: dict) -> Tuple[dict, list]:
        """
        Executes the graph by traversing nodes in breadth-first order starting from the entry point.
        The execution follows the edges based on the result of each node's execution and continues until
        it reaches a node with no outgoing edges.

        Args:
            initial_state (dict): The initial state to pass to the entry point node.

        Returns:
            Tuple[dict, list]: A tuple containing the final state and a list of execution info.
        """

        state = initial_state

        # variables for tracking execution info
        total_exec_time = 0.0
        exec_info = []
        cb_total = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": 0,
            "total_cost_USD": 0.0,
        }

        queue = deque([self.entry_point])
        while queue:
            current_node = queue.popleft()
            curr_time = time.time()
            with get_openai_callback() as callback:
                result = current_node.execute(state)
                node_exec_time = time.time() - curr_time
                total_exec_time += node_exec_time

                cb = {
                    "node_name": current_node.node_name,
                    "total_tokens": callback.total_tokens,
                    "prompt_tokens": callback.prompt_tokens,
                    "completion_tokens": callback.completion_tokens,
                    "successful_requests": callback.successful_requests,
                    "total_cost_USD": callback.total_cost,
                    "exec_time": node_exec_time,
                }

                exec_info.append(
                    cb
                )

                cb_total["total_tokens"] += cb["total_tokens"]
                cb_total["prompt_tokens"] += cb["prompt_tokens"]
                cb_total["completion_tokens"] += cb["completion_tokens"]
                cb_total["successful_requests"] += cb["successful_requests"]
                cb_total["total_cost_USD"] += cb["total_cost_USD"]

                # Do not execute the graph from this point on if previous node gave a signal
                if 'skip_branch' in result:
                    print(f"---- Not executing sub-graph since {current_node.node_name} \
                    raised a stop signal ---")
                elif current_node in self.edges:
                    current_node_connections = self.edges[current_node]
                    if current_node.node_type == 'conditional_node':
                        # Assert that there are exactly two out edges from the conditional node
                        if len(current_node_connections) != 2:
                            raise ValueError(f"Conditional node should have exactly two out connections {current_node_connections.node_name}")
                        if result["next_node"] == 0:
                            queue.append(current_node_connections[0])
                        else:
                            queue.append(current_node_connections[1])
                        # remove the conditional node result
                        del result["next_node"]
                    else:
                        queue.extend(node for node in current_node_connections)


                exec_info.append({
                    "node_name": "TOTAL RESULT",
                    "total_tokens":  cb_total["total_tokens"],
                    "prompt_tokens":  cb_total["prompt_tokens"],
                    "completion_tokens": cb_total["completion_tokens"],
                    "successful_requests": cb_total["successful_requests"],
                    "total_cost_USD":   cb_total["total_cost_USD"],
                    "exec_time": total_exec_time,
                })

        return state, exec_info
