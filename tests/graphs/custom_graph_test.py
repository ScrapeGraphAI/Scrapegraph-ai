""" 
Module for testing the class custom_graph class
"""
import unittest
import os
from dotenv import load_dotenv
from scrapegraphai.models import OpenAI
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchHTMLNode, ParseHTMLNode, GenerateAnswerNode


class TestCustomGraph(unittest.TestCase):
    """ 
    class for testing the class custom_graph
    """

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        openai_key = os.getenv("OPENAI_APIKEY")
        llm_config = {
            "api_key": openai_key,
            "model_name": "gpt-3.5-turbo",
            "temperature": 0,
            "streaming": True
        }
        cls.model = OpenAI(llm_config)
        cls.fetch_html_node = FetchHTMLNode("fetch_html")
        cls.parse_document_node = ParseHTMLNode("parse_document")
        cls.generate_answer_node = GenerateAnswerNode(
            cls.model, "generate_answer")
        cls.graph = BaseGraph(
            nodes={
                cls.fetch_html_node,
                cls.parse_document_node,
                cls.generate_answer_node
            },
            edges={
                (cls.fetch_html_node, cls.parse_document_node),
                (cls.parse_document_node, cls.generate_answer_node)
            },
            entry_point=cls.fetch_html_node
        )

    def test_execution(self):
        """ 
        Execution of the test
        """
        inputs = {"user_input": "Give me the news",
                  "url": "https://www.ansa.it/sito/notizie/topnews/index.shtml"}
        result = self.graph.execute(inputs)
        answer = result.get("answer", "No answer found.")
        self.assertIsNotNone(answer)
        self.assertNotEqual(answer, "No answer found.")


if __name__ == '__main__':
    unittest.main()
