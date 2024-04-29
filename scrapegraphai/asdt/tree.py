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

    def generate_subtree_dicts(self):
        subtree_dicts = []

        def aggregate_text_under_fork(fork_node):
            text_aggregate = {
                "content": [],
                "path_to_fork": ""
            }
            for child in fork_node.children:
                if child.value == 'text':
                    text_aggregate["content"].append(child.attributes['content'])
                elif child.is_fork:
                    continue
                else:
                    for sub_child in child.children:
                        text_aggregate["content"].append(sub_child.attributes)

            text_aggregate["path_to_fork"] = fork_node.closest_fork_path
            return text_aggregate

        def process_node(node):
            if node.is_fork:
                texts = aggregate_text_under_fork(node)
                if texts["content"]:  # Only add if there's text content
                    subtree_dicts.append({
                        node.value: {
                            "text": texts,
                            "path_to_fork": texts["path_to_fork"],
                        }
                    })
            for child in node.children:
                process_node(child)

        process_node(self.root)
        return subtree_dicts
    
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
        # graph.attr(size='10,10', dpi='300')  # Set higher DPI for better image resolution
        graph.attr('node', style='filled', fontname='Helvetica')
        graph.attr('edge', fontname='Helvetica')

        add_nodes_edges(self.root, graph)
        graph.render('tree_visualization', view=True, format='svg')  # Change format to SVG for vectorized output

        return graph
    
    def __repr__(self):
        return f"Tree(root={self.root})"