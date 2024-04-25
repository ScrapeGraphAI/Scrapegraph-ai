from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, Comment
from langchain_community.document_loaders import AsyncHtmlLoader
import time

class TreeNode:
    def __init__(self, value=None, attributes=None, children=None, parent=None, depth=0):
        self.value = value
        self.attributes = attributes if attributes is not None else {}
        self.children = children if children is not None else []
        self.parent = parent
        self.depth = depth
        self.leads_to_text = False  # Initialize the flag as False
        self.root_path = self._compute_root_path()
        self.closest_fork_path = self._compute_fork_path()

    def add_child(self, child_node):
        child_node.parent = self
        child_node.depth = self.depth + 1
        self.children.append(child_node)
        child_node.update_paths()
        self.update_leads_to_text()  # Update this node if the child leads to text

    def update_paths(self):
        self.root_path = self._compute_root_path()
        self.closest_fork_path = self._compute_fork_path()

    def update_leads_to_text(self):
        # Check if any child leads to text or is a text node
        if any(child.value == 'text' or child.leads_to_text for child in self.children):
            self.leads_to_text = True
        # Update the flag up the tree
        if self.parent and not self.parent.leads_to_text:
            self.parent.update_leads_to_text()

    def _compute_root_path(self):
        path = []
        current = self
        while current.parent:
            path.append(current.value)
            current = current.parent
        path.append('root')  # Append 'root' to start of the path
        return '>'.join(reversed(path))

    def _compute_fork_path(self):
        path = []
        current = self
        while current.parent and len(current.parent.children) == 1:
            path.append(current.value)
            current = current.parent
        path.append(current.value)  # Add the fork or root node
        return '>'.join(reversed(path))
    
    def get_subtrees(self):
        # This method finds and returns subtrees rooted at this node and all descendant forks
        subtrees = []
        if self.is_fork:
            subtrees.append(Tree(root=self))
        for child in self.children:
            subtrees.extend(child.get_subtrees())
        return subtrees
    
    def __repr__(self):
        return f"TreeNode(value={self.value}, leads_to_text={self.leads_to_text}, depth={self.depth}, root_path={self.root_path}, closest_fork_path={self.closest_fork_path})"

    @property
    def is_fork(self):
        return len(self.children) > 1

    @property
    def is_leaf(self):
        return len(self.children) == 0

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

    def __repr__(self):
        return f"Tree(root={self.root})"


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
                    tree_node.add_child(TreeNode(value='text', attributes={'content': text}))
            elif isinstance(child, Tag):
                new_node = TreeNode(value=child.name, attributes=child.attrs)
                tree_node.add_child(new_node)
                self.build_dom_tree(child, new_node)

# Usage example:

loader = AsyncHtmlLoader('https://github.com/PeriniM')
document = loader.load()
html_content = document[0].page_content

curr_time = time.time()
# Instantiate a DOMTree with HTML content
dom_tree = DOMTree(html_content)
subtrees = dom_tree.get_subtrees()  # Retrieve subtrees rooted at fork nodes

print(f"Time taken to build DOM tree: {time.time() - curr_time:.2f} seconds")

# Optionally, traverse each subtree
for subtree in subtrees:
    print("Subtree rooted at:", subtree.root.value)
    # subtree.traverse(lambda node: print(node))
# Traverse the DOMTree and print each node
# dom_tree.traverse(lambda node: print(node))
