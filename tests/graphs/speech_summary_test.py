""" 
Module for testing the class SpeechSummaryGraph
"""
import unittest
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SpeechSummaryGraph


class TestSpeechSummaryGraph(unittest.TestCase):
    """ 
    class for testing the class SpeechSummaryGraph
    """

    def setUp(self):
        load_dotenv()
        openai_key = os.getenv("OPENAI_APIKEY")
        self.llm_config = {
            "api_key": openai_key,
        }
        self.curr_dir = os.path.dirname(os.path.realpath(__file__))
        self.output_file_path = os.path.join(
            self.curr_dir, "website_summary.mp3")

    def test_summary_generation(self):
        """ 
        Execution of the test
        """
        speech_summary_graph = SpeechSummaryGraph("""Make a summary of the news to be
                                                    converted to audio for 
                                                    blind people.""",
                                                  "https://www.wired.com/category/science/",
                                                  self.llm_config,
                                                  self.output_file_path)
        final_state = speech_summary_graph.run()
        result = final_state.get("answer", "No answer found.")
        self.assertIsNotNone(result)
        self.assertNotEqual(result, "No answer found.")


if __name__ == '__main__':
    unittest.main()
