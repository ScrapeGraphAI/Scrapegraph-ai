"""
Example of custom graph using existing nodes
"""

import os
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchHTMLNode, ParseHTMLNode, GenerateAnswerNode

# load the environment variables
load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")
if not openai_key:
    print("Error: OpenAI API key not found in environment variables.")

# Define the configuration for the language model
llm_config = {
    "api_key": openai_key,
    "model_name": "gpt-3.5-turbo",
    "temperature": 0,
    "streaming": True
}
model = ChatOpenAI(**llm_config)

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
inputs = {"user_input": "What is the title of the page?", "url": "https://example.com"}
result = graph.execute(inputs)

# get the answer from the result
answer = result.get("answer", "No answer found.")
print(answer)
