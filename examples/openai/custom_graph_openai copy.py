"""
Example of custom graph using existing nodes
"""

import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from scrapegraphai.models import OpenAI, OpenAIImageToText
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode, ImageToTextNode, RAGNode, GenerateAnswerOmniNode
load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-4o",
        "temperature": 0,
        "streaming": False
    },
}

# ************************************************
# Define the graph nodes
# ************************************************

llm_model = OpenAI(graph_config["llm"])
iit_model = OpenAIImageToText(graph_config["llm"])
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
image_to_text_node = ImageToTextNode(
    input="img_urls",
    output=["img_desc"],
    node_config={
        "llm_model": iit_model,
        "max_images": 4,
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
generate_answer_omni_node = GenerateAnswerOmniNode(
    input="user_prompt & (relevant_chunks | parsed_doc | doc) & img_desc",
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
        image_to_text_node,
        rag_node,
        generate_answer_omni_node,
    ],
    edges=[
        (fetch_node, parse_node),
        (parse_node, image_to_text_node),
        (image_to_text_node, rag_node),
        (rag_node, generate_answer_omni_node)
    ],
    entry_point=fetch_node
)

# ************************************************
# Execute the graph
# ************************************************

result, execution_info = graph.execute({
    "user_prompt": "List me all the projects with their titles and image links and descriptions.",
    "url": "https://perinim.github.io/projects/"
})

# get the answer from the result
result = result.get("answer", "No answer found.")
print(result)
