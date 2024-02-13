from .conditional_node import ConditionalNode

class BaseGraph:
    def __init__(self, nodes, edges, entry_point):
        self.nodes = {node.node_name: node for node in nodes}
        self.edges = self._create_edges(edges)
        self.entry_point = entry_point.node_name

    def _create_edges(self, edges):
        edge_dict = {}
        for from_node, to_node in edges:
            edge_dict[from_node.node_name] = to_node.node_name
        return edge_dict

    def execute(self, initial_state):
        current_node_name = self.entry_point
        state = initial_state

        while current_node_name is not None:
            current_node = self.nodes[current_node_name]
            result = current_node.execute(state)

            if current_node.node_type == "conditional_node":
                # For ConditionalNode, result is the next node based on the condition
                current_node_name = result
            elif current_node_name in self.edges:
                # For regular nodes, move to the next node based on the defined edges
                current_node_name = self.edges[current_node_name]
            else:
                # No further edges, end the execution
                current_node_name = None

        return state
