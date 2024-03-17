from scrapegraphai.nodes import FetchHTMLNode, ParseNode, RAGNode, GenerateAnswerNode

state = {
    "user_prompt": None,
    "url": None,
    "doc": None,
}

parse_node = ParseNode(
    input="doc & url",
    output=["parsed_doc"],
    node_name="parse_document"
    )

parse_node.execute(state)