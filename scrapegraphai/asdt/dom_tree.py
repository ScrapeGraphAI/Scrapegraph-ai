from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from .tree import Tree
from .tree_node import TreeNode

class DOMTree(Tree):
    def __init__(self, html_content):
        super().__init__()
        self.root = TreeNode('document')
        self.build_dom_tree(BeautifulSoup(html_content, 'html.parser'), self.root)

    def build_dom_tree(self, soup_node, tree_node):
        for child in soup_node.children:
            if isinstance(child, Comment):
                continue  # Skip comments
            elif isinstance(child, NavigableString):
                text = child.strip()
                if text:
                    new_node = TreeNode(value='text', attributes={'content': text})
                    tree_node.add_child(new_node)
                    new_node.finalize_node()
            elif isinstance(child, Tag):
                new_node = TreeNode(value=child.name, attributes=child.attrs)
                tree_node.add_child(new_node)
                self.build_dom_tree(child, new_node)

    def collect_text_nodes(self, exclude_script=True):
        texts = []
        metadatas = []

        def collect(node):
            # If node is a text node, collect its data
            if node.value == 'text':
                texts.append(node.attributes['content'])
                metadatas.append({
                    'root_path': node.root_path,
                    'closest_fork_path': node.closest_fork_path
                })

        # Traverse the DOM tree to collect text nodes and their metadata
        def traverse_for_text(node):
            # Skip traversal into script tags, but continue for other nodes
            if exclude_script and node.value == 'script':
                return # Skip script tags
            
            if node.leads_to_text or node.value == 'text':
                collect(node)
                for child in node.children:
                    traverse_for_text(child)

        traverse_for_text(self.root)
        return texts, metadatas

