import unittest
from scrapegraphai.models import Ollama
from scrapegraphai.nodes import SearchInternetNode

class TestSearchInternetNode(unittest.TestCase):

    def setUp(self):
        # Configuration for the graph
        self.graph_config = {
            "llm": {
                "model": "llama3",
                "temperature": 0,
                "streaming": True
            },
            "search_engine": "google",
            "max_results": 3,
            "verbose": True
        }

        # Define the model
        self.llm_model = Ollama(self.graph_config["llm"])

        # Initialize the SearchInternetNode
        self.search_node = SearchInternetNode(
            input="user_input",
            output=["search_results"],
            node_config={
                "llm_model": self.llm_model,
                "search_engine": self.graph_config["search_engine"],
                "max_results": self.graph_config["max_results"],
                "verbose": self.graph_config["verbose"]
            }
        )

    def test_execute_search_node(self):
        # Initial state
        state = {
            "user_input": "What is the capital of France?"
        }

        # Expected output
        expected_output = {
            "user_input": "What is the capital of France?",
            "search_results": [
                "https://en.wikipedia.org/wiki/Paris",
                "https://en.wikipedia.org/wiki/France",
                "https://en.wikipedia.org/wiki/%C3%8Ele-de-France"
            ]
        }

        # Execute the node
        result = self.search_node.execute(state)

        # Assert the results
        self.assertEqual(result, expected_output)

if __name__ == "__main__":
    unittest.main()
