"""
Basic example of scraping pipeline using SpeechSummaryGraph
"""

from scrapegraphai.graphs import SpeechSummaryGraph
OPENAI_API_KEY = "YOUR_API_KEY"


llm_config = {
    "api_key": OPENAI_API_KEY
}

# Save the audio to a file
AUDIO_FILE = "website_summary.mp3"
SPEECH_SUMMARY_GRAPH = SpeechSummaryGraph("Make a summary of the webpage to be converted to audio for blind people.",
                                          "https://perinim.github.io/projects/", llm_config,
                                          AUDIO_FILE)

final_state = SPEECH_SUMMARY_GRAPH.run()
print(final_state.get("answer", "No answer found."))
