"""
Example of custom graph using existing nodes
"""

import os
from dotenv import load_dotenv
from scrapegraphai.models import OpenAI
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchHTMLNode, ParseNode, RAGNode, GenerateAnswerNode

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

# fetch_html_node = FetchNode(
#     input="url | local_dir",
#     output=["doc"],
#     node_name="fetch_html"
#     )
# parse_document_node = ParseNode(
#     input="doc",
#     output=["parsed_doc"],
#     node_name="parse_document"
#     )
# split_chunks_node = SplitChunksNode(
#     input="parsed_doc | doc",
#     output=["doc_chunks"],
#     node_name="split_chunks"
#     )
# rag_node = RAGNode(
#     input="user_prompt & (doc_chunks | parsed_doc | doc)",
#     output=["relevant_doc_chunks"],
#     model=model,
#     node_name="rag"
#     )
# generate_answer_node = GenerateAnswerNode(
#     input="user_prompt & (relevant_doc_chunks | doc_chunks | parsed_doc | doc)",
#     output=["answer"],
#     model=model,
#     node_name="generate_answer"
#     )

# define the nodes for the graph
fetch_html_node = FetchHTMLNode("fetch_html")
parse_document_node = ParseNode(doc_type="html", chunks_size=4000, node_name="parse_document")
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
inputs = {"user_input": "List me the projects with their description",
          "url": "https://perinim.github.io/projects/"}
result = graph.execute(inputs)

# get the answer from the result
answer = result.get("answer", "No answer found.")
print(answer)
