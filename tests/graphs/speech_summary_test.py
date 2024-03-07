import os
import unittest
from dotenv import load_dotenv
from scrapegraphai.graphs import SpeechSummaryGraph

load_dotenv()


class TestSpeechSummaryGraph(unittest.TestCase):
    """Test class for SpeechSummaryGraph"""

    def setUp(self):
        # Define the configuration for the language model
        openai_key = os.getenv("OPENAI_APIKEY")
        llm_config = {
            "api_key": openai_key,
        }

        # Save the audio to a file
        curr_dir = os.path.dirname(os.path.realpath(__file__))
        output_file_path = os.path.join(curr_dir, "website_summary.mp3")

        # Initialize SpeechSummaryGraph instance
        self.speech_summary_graph = SpeechSummaryGraph(
            "Make a summary of the news to be converted to audio for blind people.",
            "https://www.wired.com/category/science/",
            llm_config,
            output_file_path
        )

    def test_summary_generation(self):
        """Test summary generation and audio conversion"""
        # Run the summary graph
        final_state = self.speech_summary_graph.run()
        print(final_state)

        # Check if the final state contains non-empty 'answer' key
        self.assertTrue(final_state.get("answer")
                        is not None and final_state["answer"] != "")


if __name__ == '__main__':
    unittest.main()
