from .base_node import BaseNode

class ConditionalNode(BaseNode):
    """
    A node that determines the next step in the graph's execution flow based on 
    the presence and content of a specified key in the graph's state. It extends 
    the BaseNode by adding condition-based logic to the execution process.

    This node type is used to implement branching logic within the graph, allowing 
    for dynamic paths based on the data available in the current state.

    Attributes:
        key_name (str): The name of the key in the state to check for its presence.
        next_nodes (list): A list of two node instances. The first node is chosen 
                           for execution if the key exists and has a non-empty value, 
                           and the second node is chosen if the key does not exist or 
                           is empty.

    Args:
        key_name (str): The name of the key to check in the graph's state. This is 
                        used to determine the path the graph's execution should take.
        next_nodes (list): A list containing exactly two node instances, specifying 
                           the next nodes to execute based on the condition's outcome.
        node_name (str, optional): The unique identifier name for the node. Defaults 
                                   to "ConditionalNode".

    Raises:
        ValueError: If next_nodes does not contain exactly two elements, indicating 
                    a misconfiguration in specifying the conditional paths.
    """
    
    def __init__(self, key_name, next_nodes, node_name="ConditionalNode"):
        """
        Initializes the node with the key to check and the next node names based on the condition.

        Args:
            key_name (str): The name of the key to check in the state.
            next_nodes (list): A list containing exactly two names of the next nodes.
                               The first is used if the key exists, the second if it does not.

        Raises:
            ValueError: If next_nodes does not contain exactly two elements.
        """
        
        super().__init__(node_name, "conditional_node")
        self.key_name = key_name
        if len(next_nodes) != 2:
            raise ValueError("next_nodes must contain exactly two elements.")
        self.next_nodes = next_nodes

    def execute(self, state):
        """
        Checks if the specified key is present in the state and decides the next node accordingly.

        Args:
            state (dict): The current state of the graph.

        Returns:
            str: The name of the next node to execute based on the presence of the key.
        """

        if self.key_name in state.get("keys", {}) and len(state["keys"][self.key_name]) > 0:
            return self.next_nodes[0].node_name
        else:
            return self.next_nodes[1].node_name