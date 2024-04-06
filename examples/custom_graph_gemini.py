"""
Example of custom graph using Gemini Google model
"""

import os
from dotenv import load_dotenv
from scrapegraphai.models import Gemini
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode, RAGNode, GenerateAnswerNode

load_dotenv()
gemini_key = os.getenv("GOOGLE_APIKEY")

# Define the configuration for the graph
graph_config = {
    "llm": {
        "api_key": gemini_key,
        "model": "gemini-pro",
        "temperature": 0,
        "streaming": True
    },
}

llm_model = Gemini(graph_config["llm"])

# define the nodes for the graph
fetch_node = FetchNode(
    input="url | local_dir",
    output=["doc"],
)
parse_node = ParseNode(
    input="doc",
    output=["parsed_doc"],
)
rag_node = RAGNode(
    input="user_prompt & (parsed_doc | doc)",
    output=["relevant_chunks"],
    model_config={"llm_model": llm_model},
)
generate_answer_node = GenerateAnswerNode(
    input="user_prompt & (relevant_chunks | parsed_doc | doc)",
    output=["answer"],
    model_config={"llm_model": llm_model},
)

# create the graph by defining the nodes and their connections
graph = BaseGraph(
    nodes={
        fetch_node,
        parse_node,
        rag_node,
        generate_answer_node,
    },
    edges={
        (fetch_node, parse_node),
        (parse_node, rag_node),
        (rag_node, generate_answer_node)
    },
    entry_point=fetch_node
)

# execute the graph
result = graph.execute({
    "user_prompt": "List me the projects with their description",
    "url": "https://perinim.github.io/projects/"
})

# get the answer from the result
result = result.get("answer", "No answer found.")
print(result)
