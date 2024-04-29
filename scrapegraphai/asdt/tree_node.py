from .tree import Tree

class TreeNode:
    def __init__(self, value=None, attributes=None, children=None, parent=None, depth=0):
        self.value = value
        self.attributes = attributes if attributes is not None else {}
        self.children = children if children is not None else []
        self.parent = parent
        self.depth = depth
        # Flag to track if the subtree leads to text
        self.leads_to_text = False
        # Flags to track if the subtree has a direct leaf node
        self.has_direct_leaves = False
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
        self.structure_hash = self.hash_subtree_structure(self)
        self.content_hash = self.hash_subtree_content(self)

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

    def finalize_node(self):
        if self.is_text and self.is_leaf:
            self.update_direct_leaves_flag()

    def update_direct_leaves_flag(self):
        ancestor = self.parent
        while ancestor and len(ancestor.children) == 1:
            ancestor = ancestor.parent
        if ancestor and ancestor.is_fork:
            ancestor.has_direct_leaves = True

    def get_subtrees(self, direct_leaves=False):
        # This method finds and returns subtrees rooted at this node and all descendant forks
        # Optionally filters to include only those with direct leaves beneath fork nodes
        subtrees = []
        if self.is_fork and (not direct_leaves or self.has_direct_leaves):
            subtrees.append(Tree(root=self))
        for child in self.children:
            subtrees.extend(child.get_subtrees(direct_leaves=direct_leaves))
        return subtrees

    def hash_subtree_structure(self, node):
        """ Recursively generate a hash for the subtree structure. """
        if node.is_leaf:
            return hash((node.value,))  # Simple hash for leaf nodes
        child_hashes = tuple(self.hash_subtree_structure(child) for child in node.children)
        return hash((node.value, child_hashes))

    def hash_subtree_content(self, node):
        """ Generate a hash based on the concatenated text of the subtree. """
        text_content = self.get_all_text(node).lower().strip()
        return hash(text_content)

    def get_all_text(self, node):
        """ Recursively get all text from a node and its descendants. """
        text = node.attributes.get('content', '') if node.value == 'text' else ''
        for child in node.children:
            text += self.get_all_text(child)
        return text

    def __repr__(self):
        return f"TreeNode(value={self.value}, leads_to_text={self.leads_to_text}, is_fork={self.is_fork})"

    @property
    def is_fork(self):
        return len(self.children) > 1

    @property
    def is_leaf(self):
        return len(self.children) == 0
    
    @property
    def is_text(self):
        return self.value == 'text'