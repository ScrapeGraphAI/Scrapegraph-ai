"""
Example of custom graph using existing nodes
"""
import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchNode, ParseNode, RAGNode, GenerateAnswerNode, RobotsNode

load_dotenv()

# ************************************************
# Define the configuration for the graph
# ************************************************

mistral_key = os.getenv("MISTRAL_API_KEY")
graph_config = {
     "llm": {
        "api_key": mistral_key,
        "model": "mistralai/open-mistral-nemo",
    },
}

# ************************************************
# Define the graph nodes
# ************************************************

llm_model = ChatMistralAI(**graph_config["llm"])
embedder = MistralAIEmbeddings(api_key=llm_model.mistral_api_key)

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
    output=["doc"],
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
