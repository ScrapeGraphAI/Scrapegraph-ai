"""
Example of custom graph using existing nodes
"""

import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode, RAGNode, GenerateAnswerNode, RobotsNode
from langchain_community.llms import HuggingFaceEndpoint
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************


HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')

repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

llm_model_instance = HuggingFaceEndpoint(
    repo_id=repo_id, max_length=128, temperature=0.5, token=HUGGINGFACEHUB_API_TOKEN
)

embedder_model_instance = HuggingFaceInferenceAPIEmbeddings(
    api_key=HUGGINGFACEHUB_API_TOKEN, model_name="sentence-transformers/all-MiniLM-l6-v2"
)

graph_config = {
    "llm": {"model_instance": llm_model_instance},
}

# ************************************************
# Define the graph nodes
# ************************************************

llm_model = OpenAI(graph_config["llm"])
embedder = OpenAIEmbeddings(api_key=llm_model.openai_api_key)

# define the nodes for the graph
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
    "user_prompt": "Describe the content",
    "url": "https://example.com/"
})

# get the answer from the result
result = result.get("answer", "No answer found.")
print(result)
