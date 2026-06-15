import unittest
from unittest.mock import MagicMock, patch

from langchain_ollama import ChatOllama

from scrapegraphai.nodes import SearchInternetNode


class TestSearchInternetNode(unittest.TestCase):
    def setUp(self):
        # Configuration for the graph
        self.graph_config = {
            "llm": {"model": "llama3", "temperature": 0, "streaming": True},
            "search_engine": "duckduckgo",
            "max_results": 3,
            "verbose": True,
        }

        # Define the model (constructed with keyword arguments)
        self.llm_model = ChatOllama(**self.graph_config["llm"])

        # Initialize the SearchInternetNode
        self.search_node = SearchInternetNode(
            input="user_input",
            output=["search_results"],
            node_config={
                "llm_model": self.llm_model,
                "search_engine": self.graph_config["search_engine"],
                "max_results": self.graph_config["max_results"],
                "verbose": self.graph_config["verbose"],
            },
        )

    def test_execute_search_node(self):
        # Initial state
        state = {"user_input": "What is the capital of France?"}

        expected_results = [
            "https://en.wikipedia.org/wiki/Paris",
            "https://en.wikipedia.org/wiki/France",
            "https://en.wikipedia.org/wiki/%C3%8Ele-de-France",
        ]

        # Expected output
        expected_output = {
            "user_input": "What is the capital of France?",
            "search_results": expected_results,
        }

        # Mock the LLM chain so it returns a deterministic search query without
        # contacting a real Ollama server, and mock the web search itself.
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = ["capital of France"]

        with patch(
            "scrapegraphai.nodes.search_internet_node.PromptTemplate"
        ) as mock_prompt, patch(
            "scrapegraphai.nodes.search_internet_node.search_on_web",
            return_value=expected_results,
        ) as mock_search:
            # search_prompt | llm_model | output_parser -> mock_chain
            mock_prompt.return_value.__or__.return_value.__or__.return_value = mock_chain

            result = self.search_node.execute(state)

        # Assert the results
        self.assertEqual(result, expected_output)
        mock_search.assert_called_once()


if __name__ == "__main__":
    unittest.main()
