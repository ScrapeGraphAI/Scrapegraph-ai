""" 
Module for making the tests
"""
import os
from dotenv import load_dotenv
from scrapegraphai.models import OpenAI
from scrapegraphai.nodes import FetchNode, ParseNode, RAGNode, GenerateAnswerNode

load_dotenv()

# Define the configuration for the language model
openai_key = os.getenv("OPENAI_APIKEY")

llm_config = {
    "api_key": openai_key,
    "model_name": "gpt-3.5-turbo",
    "temperature": 0,
    "streaming": True
}
llm_model = OpenAI(llm_config)

state = {
    "user_prompt": "List me all the projects",
    "url": "https://perinim.github.io/projects/",
}

fetch_node = FetchNode(
    input="url | local_dir",
    output=["doc"],
    node_name="fetch_html"
)

updated_state = fetch_node.execute(state)
parse_node = ParseNode(
    input="doc",
    output=["parsed_doc"],
    node_name="parse_document"
)

updated_state = parse_node.execute(updated_state)

rag_node = RAGNode(
    input="user_prompt & (parsed_doc | doc)",
    output=["relevant_chunks"],
    model_config={"llm_model": llm_model},
    node_name="rag_node"
)

updated_state = rag_node.execute(updated_state)

generate_answer_node = GenerateAnswerNode(
    input="user_prompt & (relevant_chunks | parsed_doc | doc)",
    output=["answer"],
    model_config={"llm_model": llm_model},
    node_name="generate_answer"
)

print(generate_answer_node.execute(updated_state))
