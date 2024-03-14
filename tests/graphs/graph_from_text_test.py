""" 
Module for testing the graph_from_text_example
"""
import os
import unittest
from unittest.mock import patch
from scrapegraphai.models import OpenAI
from scrapegraphai.graphs import BaseGraph
from scrapegraphai.nodes import FetchTextNode, ParseNode, RAGNode, GenerateAnswerNodeFromRag


class TestCustomGraph(unittest.TestCase):
    """
    Test suite for custom graph functionality.
    """

    @patch.object(OpenAI, 'generate')
    def test_answer_generation(self, mock_generate):
        """
        Test answer generation functionality.

        Args:
            mock_generate (MagicMock): Mocked generate method of OpenAI class.
        """
        # Mock responses from the RAG and OpenAI models
        mock_generate.side_effect = [
            ("Here's the answer from the RAG model."),
            ("The final refined answer.")
        ]

        # Sample text data
        test_text = "This is a sample text for testing. It contains some information."

        # Prepare a temporary file
        with open('text_example.txt', 'w') as f:
            f.write(test_text)

        # Retrieve OpenAI API key from environment variables
        openai_key = os.getenv("OPENAI_APIKEY")

        # Check if the key was found
        if not openai_key:
            raise ValueError(
                "OPENAI_APIKEY environment variable not found. Please set it before running.")

        # LLM configuration
        llm_config = {
            "api_key": openai_key,
            "model_name": "gpt-3.5-turbo",
            "temperature": 0,
            "streaming": True
        }

        # Create the OpenAI model instance
        model = OpenAI(llm_config)

        # Set up graph structure
        fetch_text_node = FetchTextNode("load_html_from_text")
        parse_document_node = ParseNode(
            doc_type="text", chunks_size=20, node_name="parse_document")
        rag_node = RAGNode(model, "rag")
        generate_answer_node = GenerateAnswerNodeFromRag(model, "generate_answer")

        graph = BaseGraph(
            nodes={
                fetch_text_node,
                parse_document_node,
                rag_node,
                generate_answer_node
            },
            edges={
                (fetch_text_node, parse_document_node),
                (parse_document_node, rag_node),
                (rag_node, generate_answer_node)
            },
            entry_point=fetch_text_node
        )

        # Execute the graph
        inputs = {"user_input": "What is the information in this text?",
                  "text": 'text_example.txt'}
        result = graph.execute(inputs)

        # Assert the expected answer
        answer = result.get("answer", "No answer found.")
        self.assertEqual(answer, "The final refined answer.")

        # Clean up
        os.remove('text_example.txt')


if __name__ == '__main__':
    unittest.main()
