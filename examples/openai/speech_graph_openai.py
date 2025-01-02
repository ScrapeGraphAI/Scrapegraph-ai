""" 
Basic example of scraping pipeline using SpeechSummaryGraph
"""
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SpeechGraph
from scrapegraphai.utils import prettify_exec_info

load_dotenv()

# ************************************************
# Define audio output path
# ************************************************

FILE_NAME = "website_summary.mp3"
curr_dir = os.path.dirname(os.path.realpath(__file__))
output_path = os.path.join(curr_dir, FILE_NAME)

# ************************************************
# Define the configuration for the graph
# ************************************************

openai_key = os.getenv("OPENAI_APIKEY")

graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "openai/gpt-4o",
        "temperature": 0.7,
    },
    "tts_model": {
        "api_key": openai_key,
        "model": "tts-1",
        "voice": "alloy"
    },
    "output_path": output_path,
}

# ************************************************
# Create the SpeechGraph instance and run it
# ************************************************

speech_graph = SpeechGraph(
    prompt="Make a detailed audio summary of the projects.",
    source="https://perinim.github.io/projects/",
    config=graph_config,
)

result = speech_graph.run()
print(result)

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = speech_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
