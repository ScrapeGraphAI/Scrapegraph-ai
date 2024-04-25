from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, Comment
from langchain_community.document_loaders import AsyncHtmlLoader
import time

def hash_subtree_structure(node):
    """ Recursively generate a hash for the subtree structure. """
    if node.is_leaf:
        return hash((node.value,))  # Simple hash for leaf nodes
    child_hashes = tuple(hash_subtree_structure(child) for child in node.children)
    return hash((node.value, child_hashes))

def hash_subtree_content(node):
    """ Generate a hash based on the concatenated text of the subtree. """
    text_content = get_all_text(node).lower().strip()
    return hash(text_content)

def get_all_text(node):
    """ Recursively get all text from a node and its descendants. """
    text = node.attributes.get('content', '') if node.value == 'text' else ''
    for child in node.children:
        text += get_all_text(child)
    return text

class TreeNode:
    def __init__(self, value=None, attributes=None, children=None, parent=None, depth=0):
        self.value = value
        self.attributes = attributes if attributes is not None else {}
        self.children = children if children is not None else []
        self.parent = parent
        self.depth = depth
        self.leads_to_text = False
        self.root_path = self._compute_root_path()
        self.closest_fork_path = self._compute_fork_path()
        self.structure_hash = None
        self.content_hash = None

    def add_child(self, child_node):
        child_node.parent = self
        child_node.depth = self.depth + 1
        self.children.append(child_node)
        child_node.update_paths()
        self.update_leads_to_text()
        self.update_hashes()  # Update hashes when the structure changes

    def update_hashes(self):
        self.structure_hash = hash_subtree_structure(self)
        self.content_hash = hash_subtree_content(self)

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

def index_subtrees(subtrees):
    from collections import defaultdict
    structure_index = defaultdict(list)
    content_index = defaultdict(list)

    for subtree in subtrees:
        structure_hash = subtree.root.structure_hash
        content_hash = subtree.root.content_hash

        structure_index[structure_hash].append(subtree)
        content_index[content_hash].append(subtree)

    return structure_index, content_index

def find_matching_subtrees(index):
    matches = []
    for hash_key, subtrees in index.items():
        if len(subtrees) > 1:
            # Generate pairs of matched subtrees
            for i in range(len(subtrees)):
                for j in range(i + 1, len(subtrees)):
                    matches.append((subtrees[i], subtrees[j]))
    return matches

def print_subtree_details(subtree):
    """ A helper function to print subtree details for comparison. """
    nodes = []
    subtree.traverse(lambda node: nodes.append(f"{node.value}: {node.attributes.get('content', '')}"))
    return " | ".join(nodes)

def print_matches_side_by_side(matches):
    for match_pair in matches:
        subtree1, subtree2 = match_pair
        subtree1_details = print_subtree_details(subtree1)
        subtree2_details = print_subtree_details(subtree2)
        print("Match Pair:")
        print("Subtree 1:", subtree1_details)
        print("Subtree 2:", subtree2_details)
        print("\n" + "-"*100 + "\n")

# Usage example:

loader = AsyncHtmlLoader('https://perinim.github.io/projects/')
document = loader.load()
html_content = document[0].page_content

curr_time = time.time()
# Instantiate a DOMTree with HTML content
dom_tree = DOMTree(html_content)
subtrees = dom_tree.get_subtrees()  # Retrieve subtrees rooted at fork nodes

# Index subtrees by structure and content
structure_index, content_index = index_subtrees(subtrees)

# Find matches based on structure
structure_matches = find_matching_subtrees(structure_index)
print("Structure-based matches found:", len(structure_matches))

# Print structure-based matches side by side
print_matches_side_by_side(structure_matches)

# Optionally, do the same for content-based matches if needed
content_matches = find_matching_subtrees(content_index)
print("Content-based matches found:", len(content_matches))
print_matches_side_by_side(content_matches)

print(f"Time taken to build DOM tree: {time.time() - curr_time:.2f} seconds")

# Optionally, traverse each subtree
# for subtree in subtrees:
#     print("Subtree rooted at:", subtree.root.value)
    # subtree.traverse(lambda node: print(node))
# Traverse the DOMTree and print each node
# dom_tree.traverse(lambda node: print(node))
