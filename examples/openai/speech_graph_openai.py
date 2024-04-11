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
        "model": "gpt-3.5-turbo",
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
    prompt="Give me a gift idea for a friend.",
    source="https://www.amazon.it/s?k=profumo&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=17UXSZNCS2NKE&sprefix=profumo%2Caps%2C88&ref=nb_sb_noss_1",
    config=graph_config,
)

result = speech_graph.run()
print(result.get("answer", "No answer found"))

# ************************************************
# Get graph execution info
# ************************************************

graph_exec_info = speech_graph.get_execution_info()
print(prettify_exec_info(graph_exec_info))
