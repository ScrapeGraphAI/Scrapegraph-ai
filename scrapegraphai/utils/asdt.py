from bs4 import BeautifulSoup, NavigableString
from graphviz import Digraph
from langchain_community.document_loaders import AsyncHtmlLoader

def tag_structure(tag, include_scripts=True):
    """
    Recursively get a tag's structure, including its attributes, children, and textual content.
    :param tag: BeautifulSoup tag object
    :param include_scripts: Include or exclude <script> tags from the structure
    :return: A dict with the tag's name, attributes, children, and text
    """
    if isinstance(tag, NavigableString):
        return tag.strip() if tag.strip() else None

    # Skip script tags if include_scripts is False
    if not include_scripts and tag.name == 'script':
        return None

    tag_info = {
        'attrs': dict(tag.attrs),
        'children': []
    }

    for child in tag.children:
        child_structure = tag_structure(child, include_scripts=include_scripts)
        if child_structure:
            tag_info['children'].append(child_structure)

    return {tag.name: tag_info}

# Function to recursively traverse the structured HTML dictionary and create graph nodes and edges
def add_nodes_edges(graph, structure, parent=None, include_scripts=True):
    if isinstance(structure, dict):
        for tag, content in structure.items():
            # Skip script tags if include_scripts is False
            if tag == 'script' and not include_scripts:
                continue

            node_name = f"{tag}_{id(content)}"  # Unique node name
            graph.node(node_name, label=tag)
            if parent:
                graph.edge(parent, node_name)
            # Recursively process the children nodes
            add_nodes_edges(graph, content['children'], parent=node_name, include_scripts=include_scripts)

    elif isinstance(structure, list):
        for item in structure:
            add_nodes_edges(graph, item, parent, include_scripts=include_scripts)

    elif isinstance(structure, str) and parent:
        # Adding text node with limited length to keep the visualization clean
        text_label = (structure[:30] + '..') if len(structure) > 30 else structure
        text_node_name = f"text_{id(structure)}"
        graph.node(text_node_name, label=text_label, shape="plaintext")
        graph.edge(parent, text_node_name)

def has_text_content(structure):
    if isinstance(structure, str) and structure.strip():
        return True
    elif isinstance(structure, dict):
        for content in structure.values():
            if any(has_text_content(child) for child in content['children']):
                return True
    return False

def add_text_nodes_only(graph, structure, parent=None, include_scripts=True):
    """
    Recursively traverse the structured HTML dictionary and create graph nodes and edges
    for text content only.
    :param graph: Graphviz Digraph object
    :param structure: Structured HTML dictionary
    :param parent: ID of the parent node
    :param include_scripts: Include or exclude <script> tags from the visualization
    """
    if isinstance(structure, dict):
        for tag, content in structure.items():
            # Skip script tags if include_scripts is False
            if not include_scripts and tag == 'script':
                continue

            has_text = any(has_text_content(child) for child in content['children'])
            if has_text:
                node_name = f"{tag}_{id(content)}"
                graph.node(node_name, label=tag)
                if parent:
                    graph.edge(parent, node_name)
                for child in content['children']:
                    add_text_nodes_only(graph, child, parent=node_name, include_scripts=include_scripts)
    elif isinstance(structure, str) and structure.strip():
        text_label = (structure[:30] + '..') if len(structure) > 30 else structure
        text_node_name = f"text_{id(structure)}"
        graph.node(text_node_name, label=text_label, shape="plaintext")
        if parent:
            graph.edge(parent, text_node_name)

loader = AsyncHtmlLoader('https://perinim.github.io/projects/')
document = loader.load()
html_content = document[0].page_content
# Parse HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Generate and print structured HTML
html_structure = tag_structure(soup.find('html'))
# print(structure)

# Create a Digraph object
dot = Digraph()
dot.attr(rankdir='LR')  # Left to Right, change to 'TB' for Top to Bottom

# Recursively add nodes and edges based on the structured HTML dictionary
# add_nodes_edges(dot, html_structure, include_scripts=False)
add_text_nodes_only(dot, html_structure, include_scripts=False)
# Render the graph to a file and view it
dot.render('html_structure', view=True, format='png')