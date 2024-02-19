import os
from dotenv import load_dotenv
from scrapegraphai.builders import GraphBuilder

load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")
if not openai_key:
    print("Error: OpenAI API key not found in environment variables.")

# Define the configuration for the language model
llm_config = {
    "api_key": openai_key,
    "model_name": "gpt-3.5-turbo",
    "temperature": 0,
    "streaming": True
}

# Example usage of GraphBuilder
user_prompt = "I want to scrape all the links related to the cinema UCI and return me a JSON with the results."
graph_builder = GraphBuilder(user_prompt, llm_config)
graph_json = graph_builder.build_graph()

# Convert the resulting JSON to Graphviz format
graphviz_graph = graph_builder.convert_json_to_graphviz(graph_json)
graphviz_graph.render('custom_graph', view=True)
