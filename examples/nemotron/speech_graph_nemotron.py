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

nemotron_key = os.getenv("NEMOTRON_APIKEY")

graph_config = {
    "llm": {
        "api_key": nemotron_key,
        "model": "nvidia/meta/llama3-70b-instruct",
    },
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
