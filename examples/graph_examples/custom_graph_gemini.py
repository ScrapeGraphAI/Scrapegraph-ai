"""
Example of custom graph using existing node using Gemini APIs
"""

import os
from dotenv import load_dotenv
from scrapegraphai.models import Gemini
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchHTMLNode, ParseNode, GenerateAnswerNodeVanilla


load_dotenv()

gemini_key = os.getenv("GOOGLE_API_KEY")
llm_config = {
    "api_key": gemini_key,
    "model_name": "gemini-pro",
}

model = Gemini(llm_config)

# define the nodes for the graph
fetch_html_node = FetchHTMLNode("fetch_html")
parse_document_node = ParseNode(
    doc_type="html", chunks_size=4000, node_name="parse_document")
generate_answer_node = GenerateAnswerNodeVanilla(model, "generate_answer")

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
inputs = {"user_input": "List me the projects with their description",
          "url": "https://perinim.github.io/projects/"}
result = graph.execute(inputs)

# get the answer from the result
answer = result.get("answer", "No answer found.")
print(answer)
