""" 
Example of graph builder
"""
import os
from dotenv import load_dotenv
from scrapegraphai.builders import GraphBuilder

load_dotenv()

# Define the configuration for the language model
openai_key = os.getenv("OPENAI_APIKEY")
llm_config = {
    "api_key": openai_key,
    "model_name": "gpt-3.5-turbo",
    "temperature": 0,
    "streaming": True
}

# Example usage of GraphBuilder
USER_PROMPT = "Extract the news and generate a text summary with a voiceover."
graph_builder = GraphBuilder(USER_PROMPT, llm_config)
graph_json = graph_builder.build_graph()

# Convert the resulting JSON to Graphviz format
graphviz_graph = graph_builder.convert_json_to_graphviz(graph_json)

# Save the graph to a file and open it in the default viewer
graphviz_graph.render('ScrapeGraphAI_generated_graph', view=True)
