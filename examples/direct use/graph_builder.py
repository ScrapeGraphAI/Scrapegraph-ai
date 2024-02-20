""" 
Example of graph building
"""
from scrapegraphai.builders import GraphBuilder
OPENAI_API_KEY = "YOUR_API_KEY"


llm_config = {
    "api_key": OPENAI_API_KEY,
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

print(graph_json)
