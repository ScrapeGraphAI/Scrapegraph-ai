"""
Example of custom graph using existing nodes
"""

import json

from dotenv import load_dotenv

from langchain_aws import BedrockEmbeddings
from scrapegraphai.models import Bedrock
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import (
    FetchNode,
    ParseNode,
    RAGNode,
    GenerateAnswerNode,
    RobotsNode
)

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

graph_config = {
    "llm": {
        "model": "bedrock/anthropic.claude-3-sonnet-20240229-v1:0",
        "temperature": 0.0
    },
    "embeddings": {
        "model": "bedrock/cohere.embed-multilingual-v3"
    }
}

# ************************************************
# Define the graph nodes
# ************************************************

llm_model = Bedrock({
    'model_id': graph_config["llm"]["model"].split("/")[-1],
    'model_kwargs': {
        'temperature': 0.0
    }})
embedder = BedrockEmbeddings(model_id=graph_config["embeddings"]["model"].split("/")[-1])

# Define the nodes for the graph
robot_node = RobotsNode(
    input="url",
    output=["is_scrapable"],
    node_config={
        "llm_model": llm_model,
        "force_scraping": True,
        "verbose": True,
    }
)

fetch_node = FetchNode(
    input="url | local_dir",
    output=["doc", "link_urls", "img_urls"],
    node_config={
        "verbose": True,
        "headless": True,
    }
)

parse_node = ParseNode(
    input="doc",
    output=["parsed_doc"],
    node_config={
        "chunk_size": 4096,
        "verbose": True,
    }
)

rag_node = RAGNode(
    input="user_prompt & (parsed_doc | doc)",
    output=["relevant_chunks"],
    node_config={
        "llm_model": llm_model,
        "embedder_model": embedder,
        "verbose": True,
    }
)

generate_answer_node = GenerateAnswerNode(
    input="user_prompt & (relevant_chunks | parsed_doc | doc)",
    output=["answer"],
    node_config={
        "llm_model": llm_model,
        "verbose": True,
    }
)

# ************************************************
# Create the graph by defining the connections
# ************************************************

graph = BaseGraph(
    nodes=[
        robot_node,
        fetch_node,
        parse_node,
        rag_node,
        generate_answer_node,
    ],
    edges=[
        (robot_node, fetch_node),
        (fetch_node, parse_node),
        (parse_node, rag_node),
        (rag_node, generate_answer_node)
    ],
    entry_point=robot_node
)

# ************************************************
# Execute the graph
# ************************************************

result, execution_info = graph.execute({
    "user_prompt": "List me all the articles",
    "url": "https://perinim.github.io/projects"
})

# Get the answer from the result
result = result.get("answer", "No answer found.")
print(json.dumps(result, indent=4))
