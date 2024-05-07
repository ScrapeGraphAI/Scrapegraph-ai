""" 
Module for creating the tree
"""
import time
from bs4 import BeautifulSoup, NavigableString
from graphviz import Digraph
from langchain_community.document_loaders import AsyncHtmlLoader
from bs4 import BeautifulSoup, NavigableString, Comment
from remover import remover

def tag_structure(tag, exclude=None) -> dict:
    """
    Recursively get a tag's structure, including its attributes, children, and textual content,
    with an option to exclude specific tags. Text is treated as separate nodes.

    :param tag: BeautifulSoup tag object
    :param exclude: List of tag names to exclude from the structure
    :return: A dict with the tag's name, attributes, children, and text nodes
    """
    if exclude is None:
        exclude = []

    if isinstance(tag, Comment):
        return None  # Ignore comments

    if isinstance(tag, NavigableString):
        text_content = tag.strip()
        if text_content:
            text_node = {'text': {
                'content': text_content,
                'children': []
            }
            }
            return text_node
        else:
            return None

    if tag.name in exclude:
        return None  # Skip tags specified in the exclude list

    tag_info = {
        'attrs': dict(tag.attrs),
        'children': []
    }

    for child in tag.children:
        child_structure = tag_structure(child, exclude=exclude)
        if child_structure:
            # Append structure or text node to children
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
            add_nodes_edges(
                graph, content['children'], parent=node_name, include_scripts=include_scripts)

    elif isinstance(structure, list):
        for item in structure:
            add_nodes_edges(graph, item, parent,
                            include_scripts=include_scripts)

    elif isinstance(structure, str) and parent:
        # Adding text node with limited length to keep the visualization clean
        text_label = (structure[:30] +
                      '..') if len(structure) > 30 else structure
        text_node_name = f"text_{id(structure)}"
        graph.node(text_node_name, label=text_label, shape="plaintext")
        graph.edge(parent, text_node_name)


def has_text_content(structure):
    if isinstance(structure, str) and structure.strip():
        # If it's a string with non-whitespace characters, it's text content
        return True
    elif isinstance(structure, dict):

        for key, value in structure.items():
            if isinstance(value, list):
                # It's a list, probably of children
                if any(has_text_content(child) for child in value):
                    return True
            elif isinstance(value, dict):
                # It's a dictionary, need to check recursively
                if has_text_content(value):
                    return True
    return False


def add_text_nodes_only(graph, structure, parent=None):
    """
    Recursively traverse the structured HTML dictionary and create graph nodes and edges
    for text content only, using Graphviz Digraph object.
    :param graph: Graphviz Digraph object
    :param structure: Structured HTML dictionary
    :param parent: ID of the parent node
    :param include_scripts: Include or exclude <script> tags from the visualization
    """
    if isinstance(structure, dict):
        for tag, content in structure.items():

            if 'text' in content:
                # Content is a text node
                text_label = (
                    content['text'][:30] + '...') if len(content['text']) > 30 else content['text']
                text_node_name = f"text_{id(content)}"
                graph.node(text_node_name, label=text_label, shape="plaintext")
                if parent:
                    graph.edge(parent, text_node_name)
            else:
                # Content is a tag with children
                node_name = f"{tag}_{id(content)}"
                graph.node(node_name, label=tag)
                if parent:
                    graph.edge(parent, node_name)
                for child in content.get('children', []):
                    add_text_nodes_only(graph, child, parent=node_name)


loader = AsyncHtmlLoader('https://perinim.github.io/projects/')
document = loader.load()
html_content = remover(document[0].page_content)

curr_time = time.time()
# Parse HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Generate and print structured HTML
html_structure = tag_structure(soup, exclude=[
                               'head', 'style', 'script'])
print(
    f"Time taken to generate structured HTML: {time.time() - curr_time:.2f} seconds")
# print(json.dumps(html_structure, indent=2))

# Create a Digraph object
dot = Digraph()
dot.attr(rankdir='LR')  # Left to Right, change to 'TB' for Top to Bottom

# Recursively add nodes and edges based on the structured HTML dictionary
# add_nodes_edges(dot, html_structure, include_scripts=False)
add_text_nodes_only(dot, html_structure)
# Render the graph to a file and view it
dot.render('html_structure', view=True, format='png')
