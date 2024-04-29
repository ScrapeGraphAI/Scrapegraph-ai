from langchain_community.document_loaders import AsyncHtmlLoader
import time
from scrapegraphai.asdt import DOMTree

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

# *********************************************************************************************************************
# Usage example:
# *********************************************************************************************************************

loader = AsyncHtmlLoader('https://perinim.github.io/projects/')
document = loader.load()
html_content = document[0].page_content

curr_time = time.time()
# Instantiate a DOMTree with HTML content
dom_tree = DOMTree(html_content)
# nodes, metadatas = dom_tree.collect_text_nodes()  # Collect text nodes for analysis
# for node, metadata in zip(nodes, metadatas):
#     print("Text:", node)
#     print("Metadata:", metadata)

# sub_list = dom_tree.generate_subtree_dicts()  # Generate subtree dictionaries for analysis
# print(sub_list)
# graph = dom_tree.visualize(exclude_tags=['script', 'style', 'meta', 'link'])
subtrees = dom_tree.get_subtrees()  # Retrieve subtrees rooted at fork nodes
print("Number of subtrees found:", len(subtrees))

# remove trees whos root node does not lead to any text
text_subtrees = [subtree for subtree in subtrees if subtree.root.leads_to_text]
print("Number of subtrees that lead to text:", len(text_subtrees))

direct_leaf_subtrees = [subtree for subtree in text_subtrees if subtree.root.has_direct_leaves]
print("Number of subtrees with direct leaves beneath fork nodes:", len(direct_leaf_subtrees))

for subtree in direct_leaf_subtrees:
    print("Subtree rooted at:", subtree.root.value)
    subtree.traverse(lambda node: print(node))
# Index subtrees by structure and content
# structure_index, content_index = index_subtrees(subtrees)

# # Find matches based on structure
# structure_matches = find_matching_subtrees(structure_index)
# print("Structure-based matches found:", len(structure_matches))

# # Print structure-based matches side by side
# print_matches_side_by_side(structure_matches)

# # Optionally, do the same for content-based matches if needed
# content_matches = find_matching_subtrees(content_index)
# print("Content-based matches found:", len(content_matches))
# print_matches_side_by_side(content_matches)

print(f"Time taken to build DOM tree: {time.time() - curr_time:.2f} seconds")

# Optionally, traverse each subtree
# for subtree in subtrees:
#     print("Subtree rooted at:", subtree.root.value)
#     subtree.traverse(lambda node: print(node))
# Traverse the DOMTree and print each node
# dom_tree.traverse(lambda node: print(node))
