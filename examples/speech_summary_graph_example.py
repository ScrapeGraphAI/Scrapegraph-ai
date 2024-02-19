""" 
Basic example of scraping pipeline using SpeechSummaryGraph
"""

import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SpeechSummaryGraph

load_dotenv()

# Define the configuration for the language model
openai_key = os.getenv("OPENAI_APIKEY")
llm_config = {
    "api_key": openai_key,
}

# Save the audio to a file
curr_dir = os.path.dirname(os.path.realpath(__file__))
output_file_path = os.path.join(curr_dir, "website_summary.mp3")

speech_summary_graph = SpeechSummaryGraph("Make a summary of the webpage to be converted to speech for blind people.",
                             "https://perinim.github.io/projects/", llm_config,
                                output_file_path)

final_state = speech_summary_graph.run()
print(final_state.get("answer", "No answer found."))
