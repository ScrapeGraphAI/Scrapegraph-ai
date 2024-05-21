"""
Example of custom graph using existing nodes
"""

import os
import uuid

from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from scrapegraphai.models import OpenAI
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode, RAGNode, GenerateAnswerNode
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "streaming": False
    },
}

# ************************************************
# Define the graph nodes
# ************************************************

llm_model = OpenAI(graph_config["llm"])
embedder = OpenAIEmbeddings(api_key=llm_model.openai_api_key)

# define the nodes for the graph

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
        fetch_node,
        parse_node,
        rag_node,
        generate_answer_node,
    ],
    edges=[
        (fetch_node, parse_node),
        (parse_node, rag_node),
        (rag_node, generate_answer_node)
    ],
    entry_point=fetch_node,
    use_burr=True,
    burr_config={
        "app_instance_id": str(uuid.uuid4()),
        "inputs": {
            "llm_model": graph_config["llm"].get("model", "gpt-3.5-turbo"),
        }
    }
)

# ************************************************
# Execute the graph
# ************************************************

result, execution_info = graph.execute({
    "user_prompt": "Describe the content",
    "url": "https://example.com/"
})

# get the answer from the result
result = result.get("answer", "No answer found.")
print(result)
