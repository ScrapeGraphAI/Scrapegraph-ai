""" 
Module for testing SmartScraper class
"""
import os
import unittest
from dotenv import load_dotenv
from scrapegraphai.graphs import SmartScraperGraph

load_dotenv()


class TestScrapingPipeline(unittest.TestCase):
    """Test class for SmartScraperGraph"""

    def setUp(self):
        # Define the configuration for the language model
        openai_key = os.getenv("OPENAI_APIKEY")
        llm_config = {
            "api_key": openai_key,
            "model_name": "gpt-3.5-turbo",
        }

        # Define URL and PROMPT
        url = "https://perinim.github.io/projects/"
        prompt = "List me all the titles and project descriptions"

        # Create the SmartScraperGraph instance
        self.smart_scraper_graph = SmartScraperGraph(prompt, url, llm_config)

    def test_scraping(self):
        """Main test method"""
        # Run the scraper
        result = self.smart_scraper_graph.run()
        print(result)

        # Check if the result is not empty
        self.assertNotEqual(result, {})


if __name__ == '__main__':
    unittest.main()
