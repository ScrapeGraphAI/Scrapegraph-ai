from scrapegraphai.nodes import FetchNode, ParseNode, RAGNode, GenerateAnswerNode

state = {
    "user_prompt": "List me all the projects",
    "url": "https://perinim.github.io/projects/",
}

fetch_node = FetchNode(
    input="url | local_dir",
    output=["doc"],
    node_name="fetch_html"
    )

updated_state = fetch_node.execute(state)
parse_node = ParseNode(
    input="doc",
    output=["parsed_doc"],
    node_name="parse_document"
    )

parse_node.execute(updated_state)