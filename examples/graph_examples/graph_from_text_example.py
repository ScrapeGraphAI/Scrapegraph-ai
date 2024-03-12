"""
Example of custom graph using existing nodes
"""

import os
from dotenv import load_dotenv
from scrapegraphai.models import OpenAI
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchTextNode, ParseNode, RAGNode, GenerateAnswerNode

load_dotenv()

# Define the configuration for the language model
openai_key = os.getenv("OPENAI_APIKEY")
llm_config = {
    "api_key": openai_key,
    "model_name": "gpt-3.5-turbo",
    "temperature": 0,
    "streaming": True
}
model = OpenAI(llm_config)

curr_dir = os.path.dirname(__file__)
file_path = os.path.join(curr_dir, "text_example.txt")

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()


# define the nodes for the graph
fetch_html_node = FetchTextNode("load_html_from_text")
parse_document_node = ParseNode(doc_type="text", chunks_size=4000, node_name="parse_document")
rag_node = RAGNode(model, "rag")
generate_answer_node = GenerateAnswerNode(model, "generate_answer")

# create the graph
graph = BaseGraph(
    nodes={
        fetch_html_node,
        parse_document_node,
        rag_node,
        generate_answer_node
    },
    edges={
        (fetch_html_node, parse_document_node),
        (parse_document_node, rag_node),
        (rag_node, generate_answer_node)
    },
    entry_point=fetch_html_node
)

# execute the graph
inputs = {"user_input": "Give me the name of all the news",
          "text": text}
result = graph.execute(inputs)

# get the answer from the result
answer = result.get("answer", "No answer found.")
print(answer)
