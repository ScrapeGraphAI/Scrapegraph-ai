from bs4 import BeautifulSoup, NavigableString
from pyecharts import options as opts
from pyecharts.charts import Tree
from langchain_community.document_loaders import AsyncHtmlLoader
import webbrowser


def tag_structure(tag, include_scripts=True):
    if isinstance(tag, NavigableString):
        text = tag.strip()
        return {"name": text[:30] + "..." if len(text) > 30 else text} if text else None

    if not include_scripts and tag.name == 'script':
        return None

    children = []
    for child in tag.children:
        child_structure = tag_structure(child, include_scripts=include_scripts)
        if child_structure:
            children.append(child_structure)

    tag_info = {"name": tag.name, "children": children} if children else {"name": tag.name}
    return tag_info

def build_tree_data(html_structure):
    return [html_structure] if html_structure else []

# Load and parse HTML content
loader = AsyncHtmlLoader('https://perinim.github.io/projects/')
document = loader.load()
html_content = document[0].page_content
soup = BeautifulSoup(html_content, 'html.parser')

# Generate structured HTML
html_structure = tag_structure(soup.find('html'), include_scripts=False)

# Build tree data for pyecharts
tree_data = build_tree_data(html_structure)

# Create a Tree chart
chart = Tree(init_opts=opts.InitOpts(width="100%", height="800px"))
chart.add(
    series_name="",
    data=tree_data,
    initial_tree_depth=-1,  # Set to -1 to expand all nodes initially
    layout='orthogonal',  # Can be 'radial' for radial layout
    is_roam=True,  # Allows users to zoom and pan
    # symbol_size=7,  # Adjusts the size of the nodes (optional)
)

chart.set_global_opts(
    title_opts=opts.TitleOpts(title="HTML Structure Tree"),
    tooltip_opts=opts.TooltipOpts(trigger="item", trigger_on="mousemove|click")
)

# Render the tree to HTML file
chart.render("html_structure_tree.html")
html_file_path = chart.render("html_structure_tree.html")
webbrowser.open(html_file_path)
