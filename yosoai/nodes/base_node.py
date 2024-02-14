""" 
Module for creating the basic node
"""
from abc import ABC, abstractmethod


class BaseNode(ABC):
    """
    An abstract base class for nodes in a graph-based workflow. Each node is 
    intended to perform a specific action when executed as part of the graph's 
    processing flow.

    Attributes:
        node_name (str): A unique identifier for the node.
        node_type (str): Specifies the node's type, which influences how the 
                         node interacts within the graph. Valid values are 
                         "node" for standard nodes and "conditional_node" for 
                         nodes that determine the flow based on conditions.

    Methods:
        execute(state): An abstract method that subclasses must implement. This 
                        method should contain the logic that the node executes 
                        when it is reached in the graph's flow. It takes the 
                        graph's current state as input and returns the updated 
                        state after execution.

    Args:
        node_name (str): The unique identifier name for the node. This name is 
                         used to reference the node within the graph.
        node_type (str): The type of the node, limited to "node" or 
                         "conditional_node". This categorization helps in 
                         determining the node's role and behavior within the 
                         graph.

    Raises:
        ValueError: If the provided `node_type` is not one of the allowed 
                    values ("node" or "conditional_node"), a ValueError is 
                    raised to indicate the incorrect usage.
    """

    def __init__(self, node_name: str, node_type: str):
        """
        Initialize the node with a unique identifier and a specified node type.

        Args:
            node_name (str): The unique identifier name for the node.
            node_type (str): The type of the node, limited to "node" or "conditional_node".

        Raises:
            ValueError: If node_type is not "node" or "conditional_node".
        """
        self.node_name = node_name
        if node_type not in ["node", "conditional_node"]:
            raise ValueError(
                f"node_type must be 'node' or 'conditional_node', got '{node_type}'")
        self.node_type = node_type

    @abstractmethod
    def execute(self, state: dict):
        """
        Execute the node's logic and return the updated state.
        Args:
            state (dict): The current state of the graph.
        :return: The updated state after executing this node.
        """
        pass
