import unittest

from langchain_core.runnables import RunnableParallel
from pydantic import BaseModel, Field
from requests.exceptions import Timeout
from scrapegraphai.nodes.generate_answer_node import GenerateAnswerNode
from unittest.mock import MagicMock, patch

class TestGenerateAnswerNode(unittest.TestCase):
    def setUp(self):
        self.node_config = {
            "llm_model": MagicMock(),
            "verbose": False,
            "force": False,
            "script_creator": False,
            "is_md_scraper": False,
            "timeout": 10
        }
        self.node = GenerateAnswerNode("input", ["output"], self.node_config)

    @patch.object(GenerateAnswerNode, 'invoke_with_timeout')
    def test_execute_timeout(self, mock_invoke):
        # Simulate a timeout during execution
        mock_invoke.side_effect = Timeout("Response timeout exceeded")

        # Prepare input state
        input_state = {
            "input": "test question",
            "chunks": ["chunk1", "chunk2"]
        }

        # Execute the node
        result_state = self.node.execute(input_state)

        # Check if the output contains the expected error message
        self.assertIn("output", result_state)
        self.assertIsInstance(result_state["output"], dict)
        self.assertIn("error", result_state["output"])
        self.assertEqual(result_state["output"]["error"], "Response timeout exceeded")

        # Verify that invoke_with_timeout was called
        mock_invoke.assert_called()

    @patch.object(GenerateAnswerNode, 'invoke_with_timeout')
    def test_execute_single_chunk(self, mock_invoke):
        # Prepare a mock LLM model
        mock_llm = MagicMock()

        # Configure the node
        node_config = {
            "llm_model": mock_llm,
            "verbose": False,
            "force": False,
            "script_creator": False,
            "is_md_scraper": False,
            "timeout": 10
        }
        node = GenerateAnswerNode("input", ["output"], node_config)

        # Prepare input state with a single document chunk
        input_state = {
            "input": "test question",
            "chunks": ["single chunk content"]
        }

        # Mock the response from invoke_with_timeout
        mock_invoke.return_value = "Mocked answer for single chunk"

        # Execute the node
        result_state = node.execute(input_state)

        # Assert that invoke_with_timeout was called once
        mock_invoke.assert_called_once()

        # Check if the output contains the expected answer
        self.assertIn("output", result_state)
        self.assertEqual(result_state["output"], "Mocked answer for single chunk")

        # Verify that the correct template was used (TEMPLATE_NO_CHUNKS_MD)
        call_args = mock_invoke.call_args[0]
        self.assertIn("context", call_args[1])
        self.assertEqual(call_args[1]["context"], ["single chunk content"])

    @patch('scrapegraphai.nodes.generate_answer_node.RunnableParallel')
    @patch.object(GenerateAnswerNode, 'invoke_with_timeout')
    def test_execute_multiple_chunks(self, mock_invoke, mock_runnable_parallel):
        # Prepare a mock LLM model
        mock_llm = MagicMock()

        # Configure the node
        node_config = {
            "llm_model": mock_llm,
            "verbose": False,
            "force": False,
            "script_creator": False,
            "is_md_scraper": False,
            "timeout": 10
        }
        node = GenerateAnswerNode("input", ["output"], node_config)

        # Prepare input state with multiple document chunks
        input_state = {
            "input": "test question",
            "chunks": ["chunk1 content", "chunk2 content", "chunk3 content"]
        }

        # Mock the response from RunnableParallel
        mock_runnable_parallel.return_value = MagicMock()
        mock_runnable_parallel.return_value.invoke.return_value = {
            "chunk1": "Result from chunk1",
            "chunk2": "Result from chunk2",
            "chunk3": "Result from chunk3"
        }

        # Mock the response from invoke_with_timeout for the merge step
        mock_invoke.side_effect = [
            mock_runnable_parallel.return_value.invoke.return_value,
            "Merged result from all chunks"
        ]

        # Execute the node
        result_state = node.execute(input_state)

        # Assert that invoke_with_timeout was called twice (once for chunks, once for merge)
        self.assertEqual(mock_invoke.call_count, 2)

        # Check if the output contains the expected merged answer
        self.assertIn("output", result_state)
        self.assertEqual(result_state["output"], "Merged result from all chunks")

        # Verify that RunnableParallel was created with the correct number of chains
        mock_runnable_parallel.assert_called_once()
        self.assertEqual(len(mock_runnable_parallel.call_args[1]), 3)  # 3 chunks

        # Verify that the merge step was called with the correct context
        merge_call_args = mock_invoke.call_args_list[1][0]
        self.assertIn("context", merge_call_args[1])
        self.assertEqual(merge_call_args[1]["context"], {
            "chunk1": "Result from chunk1",
            "chunk2": "Result from chunk2",
            "chunk3": "Result from chunk3"
        })

    @patch.object(GenerateAnswerNode, 'invoke_with_timeout')
    def test_execute_with_additional_info(self, mock_invoke):
        # Prepare a mock LLM model
        mock_llm = MagicMock()

        # Configure the node with additional_info
        node_config = {
            "llm_model": mock_llm,
            "verbose": False,
            "force": False,
            "script_creator": False,
            "is_md_scraper": False,
            "timeout": 10,
            "additional_info": "This is additional information: "
        }
        node = GenerateAnswerNode("input", ["output"], node_config)

        # Prepare input state with a single document chunk
        input_state = {
            "input": "test question",
            "chunks": ["single chunk content"]
        }

        # Mock the response from invoke_with_timeout
        mock_invoke.return_value = "Mocked answer with additional info"

        # Execute the node
        result_state = node.execute(input_state)

        # Assert that invoke_with_timeout was called once
        mock_invoke.assert_called_once()

        # Check if the output contains the expected answer
        self.assertIn("output", result_state)
        self.assertEqual(result_state["output"], "Mocked answer with additional info")

        # Verify that the correct template was used and includes additional_info
        call_args = mock_invoke.call_args[0]
        self.assertIn("This is additional information: ", str(call_args[0]))

        # Verify that the context is correct
        self.assertIn("context", call_args[1])
        self.assertEqual(call_args[1]["context"], ["single chunk content"])

    @patch('scrapegraphai.nodes.generate_answer_node.get_pydantic_output_parser')
    @patch.object(GenerateAnswerNode, 'invoke_with_timeout')
    def test_execute_with_custom_schema(self, mock_invoke, mock_get_parser):
        # Define a custom schema
        class CustomSchema(BaseModel):
            answer: str = Field(description="The generated answer")
            confidence: float = Field(description="Confidence score of the answer")

        # Prepare a mock L