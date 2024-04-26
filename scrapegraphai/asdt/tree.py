from graphviz import Digraph

class Tree:
    def __init__(self, root=None):
        self.root = root

    def traverse(self, visit_func):
        def _traverse(node):
            if node:
                visit_func(node)
                for child in node.children:
                    _traverse(child)
        _traverse(self.root)

    def get_subtrees(self):
        # Retrieves all subtrees rooted at fork nodes
        return self.root.get_subtrees() if self.root else []

    def visualize(self, exclude_tags = ['script']):
        def add_nodes_edges(tree_node, graph):
           if tree_node:
                # Skip excluded tags
                if tree_node.value in exclude_tags:
                    return
                
                # Format node label to include attributes
                attr_str = None
                label = f"{tree_node.value}\n[{attr_str}]" if attr_str else tree_node.value
                # Determine color based on node properties
                if tree_node.value == 'text':
                    color = 'red'  # Text nodes
                elif tree_node.is_fork:
                    color = 'green'  # Fork nodes
                elif tree_node.leads_to_text:
                    color = 'lightblue2'  # Nodes leading to text
                else:
                    color = 'white'  # Nodes that do not lead to text and are not forks
        
                # Customize node appearance
                graph.node(name=str(id(tree_node)), label=label, 
                        fontsize='12', shape='ellipse', color=color, fontcolor='black')

                if tree_node.parent:
                    graph.edge(str(id(tree_node.parent)), str(id(tree_node)), fontsize='10')

                for child in tree_node.children:
                    add_nodes_edges(child, graph)


        # Initialize Digraph, set graph and node attributes
        graph = Digraph()
        graph.attr(size='10,10', dpi='300')  # Set higher DPI for better image resolution
        graph.attr('node', style='filled', fontname='Helvetica')
        graph.attr('edge', fontname='Helvetica')

        add_nodes_edges(self.root, graph)
        graph.render('tree_visualization', view=True, format='svg')  # Change format to SVG for vectorized output

        return graph
    
    def __repr__(self):
        return f"Tree(root={self.root})"