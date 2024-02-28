""" 
Module for testing the class SmartScraperGraph
"""
import unittest
import os
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph


class TestSmartScraperGraph(unittest.TestCase):
    """ 
    class for testing the class SmartScraperGraph
    """

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        openai_key = os.getenv("OPENAI_APIKEY")
        cls.llm_config = {
            "api_key": openai_key,
            "model_name": "gpt-3.5-turbo",
        }
        cls.URL = "https://perinim.github.io/projects/"
        cls.PROMPT = "List me all the titles and project descriptions and give me an audio"
        cls.smart_scraper_graph = SmartScraperGraph(
            cls.PROMPT, cls.URL, cls.llm_config)

    def test_scraper_execution(self):
        """ 
        Execution of the test
        """
        answer = self.smart_scraper_graph.run()
        self.assertIsNotNone(answer)
        self.assertNotEqual(answer, "")


if __name__ == '__main__':
    unittest.main()
