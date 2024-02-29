""" 
Tests for the class FetchHTMLNode
"""
import os
import unittest
from dotenv import load_dotenv
from scrapegraphai.nodes import FetchHTMLNode

load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")


class TestFetchHTMLNode(unittest.TestCase):
    """ 
    Class for testing the class FetchHTMLNode
    """

    def test_initialization(self):
        """ 
        Setup of the tests
        """

        node = FetchHTMLNode("test_node")
        self.assertEqual(node.node_name, "test_node")
        self.assertEqual(node.node_type, "node")

    def test_execute(self):
        """ 
        Execution of the test
        """
        node = FetchHTMLNode("test_node")
        state = {"url": "http://example.com"}
        updated_state = node.execute(state)
        self.assertIn("document", updated_state)
        self.assertTrue(updated_state["document"])

    def test_execute_missing_url(self):
        """ 
        Test for when there are missing url
        """
        node = FetchHTMLNode("test_node")
        state = {}
        with self.assertRaises(KeyError):
            node.execute(state)


if __name__ == '__main__':
    unittest.main()
