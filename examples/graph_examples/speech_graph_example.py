""" 
Basic example of scraping pipeline using SpeechSummaryGraph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SpeechGraph

load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")

# Save the audio to a file
FILE_NAME = "website_summary.mp3"
curr_dir = os.path.dirname(os.path.realpath(__file__))
output_path = os.path.join(curr_dir, FILE_NAME)

# Define the configuration for the graph
graph_config = {
    "llm": {
        "api_key": openai_key,
        "model": "gpt-3.5-turbo",
    },
    "tts_model": {
        "api_key": openai_key,
        "model": "tts-1",
        "voice": "alloy"
    },
    "output_path": output_path,
}

speech_graph = SpeechGraph(
    prompt="Create a summary of the website",
    file_source="https://perinim.github.io/projects/",
    config=graph_config,
)

result = speech_graph.run()
print(result.get("answer", "No answer found"))
