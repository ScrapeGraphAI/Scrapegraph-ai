
"""
Example of custom graph using existing nodes
"""
from scrapegraphai.nodes import FetchHTMLNode, ParseHTMLNode, GenerateAnswerNode
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.models import OpenAI
from scrapegraphai.helpers import nodes_metadata

OPENAI_API_KEY = "YOUR_API_KEY"

# check available nodes

nodes_metadata.keys()

# to get more information about a node
print(nodes_metadata['ImageToTextNode'])

# Define the configuration for the language model
llm_config = {
    "api_key": OPENAI_API_KEY,
    "model_name": "gpt-3.5-turbo",
    "temperature": 0,
    "streaming": True
}
model = OpenAI(llm_config)

# define the nodes for the graph
fetch_html_node = FetchHTMLNode("fetch_html")
parse_document_node = ParseHTMLNode("parse_document")
generate_answer_node = GenerateAnswerNode(model, "generate_answer")

# create the graph
graph = BaseGraph(
    nodes={
        fetch_html_node,
        parse_document_node,
        generate_answer_node
    },
    edges={
        (fetch_html_node, parse_document_node),
        (parse_document_node, generate_answer_node)
    },
    entry_point=fetch_html_node
)

# execute the graph
inputs = {"user_input": "What is the title of the page?",
          "url": "https://example.com"}
result = graph.execute(inputs)

# get the answer from the result
answer = result.get("answer", "No answer found.")
print(answer)
