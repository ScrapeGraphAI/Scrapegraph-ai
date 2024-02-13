from .base_node import BaseNode

class ConditionalNode(BaseNode):
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