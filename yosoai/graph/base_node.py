from abc import ABC, abstractmethod

class BaseNode(ABC):
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
            raise ValueError(f"node_type must be 'node' or 'conditional_node', got '{node_type}'")
        self.node_type = node_type
        
    @abstractmethod
    def execute(self, state):
        """
        Execute the node's logic and return the updated state.
        
        :param state: The current state of the graph.
        :return: The updated state after executing this node.
        """
        pass