""" 
Module for implementing the conditional node
"""

from .base_node import BaseNode


class ConditionalNode(BaseNode):
    """
    A node that determines the next step in the graph's execution flow based on 
    the presence and content of a specified key in the graph's state. It extends 
    the BaseNode by adding condition-based logic to the execution process.

    This node type is used to implement branching logic within the graph, allowing 
    for dynamic paths based on the data available in the current state.

    It is expected thar exactly two edges are created out of this node.
    The first node is chosen for execution if the key exists and has a non-empty value,
    and the second node is chosen if the key does not exist or is empty.

    Attributes:
        key_name (str): The name of the key in the state to check for its presence.

    Args:
        key_name (str): The name of the key to check in the graph's state. This is 
                        used to determine the path the graph's execution should take.
        node_name (str, optional): The unique identifier name for the node. Defaults 
                                   to "ConditionalNode".

    """

    def __init__(self, key_name: str, node_name="ConditionalNode"):
        """
        Initializes the node with the key to check and the next node names based on the condition.

        Args:
            key_name (str): The name of the key to check in the state.
        """

        super().__init__(node_name, "conditional_node")
        self.key_name = key_name

    def execute(self, state: dict) -> dict:
        """
        Checks if the specified key is present in the state and decides the next node accordingly.

        Args:
            state (dict): The current state of the graph.

        Returns:
            str: The name of the next node to execute based on the presence of the key.
        """

        if self.key_name in state and len(state[self.key_name]) > 0:
            state["next_node"] = 0
        else:
            state["next_node"] = 1
        return state
