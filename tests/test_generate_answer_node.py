import json

import pytest
from langchain_community.chat_models import (
    ChatOllama,
)
from langchain_core.runnables import (
    RunnableParallel,
)
from requests.exceptions import (
    Timeout,
)

from scrapegraphai.nodes.generate_answer_node import (
    GenerateAnswerNode,
)


class DummyLLM:
    def __call__(self, *args, **kwargs):
        return "dummy response"


class DummyLogger:
    def info(self, msg):
        pass

    def error(self, msg):
        pass


@pytest.fixture
def dummy_node():
    """
    Fixture for a GenerateAnswerNode instance using DummyLLM.
    Uses a valid input keys string ("dummy_input & doc") to avoid parsing errors.
    """
    node_config = {"llm_model": DummyLLM(), "verbose": False, "timeout": 1}
    node = GenerateAnswerNode("dummy_input & doc", ["output"], node_config=node_config)
    node.logger = DummyLogger()
    node.get_input_keys = lambda state: ["dummy_input", "doc"]
    return node


def test_process_missing_content_and_user_prompt(dummy_node):
    """
    Test that process() raises a ValueError when either the content or the user prompt is missing.
    """
    state_missing_content = {"user_prompt": "What is the answer?"}
    with pytest.raises(ValueError) as excinfo1:
        dummy_node.process(state_missing_content)
    assert "No content found in state" in str(excinfo1.value)
    state_missing_prompt = {"content": "Some valid context content"}
    with pytest.raises(ValueError) as excinfo2:
        dummy_node.process(state_missing_prompt)
    assert "No user prompt found in state" in str(excinfo2.value)


class DummyLLMWithPipe:
    """DummyLLM that supports the pipe '|' operator.
    When used in a chain with a PromptTemplate, the pipe operator returns self,
    simulating chain composition."""

    def __or__(self, other):
        return self

    def __call__(self, *args, **kwargs):
        return {"content": "script single-chunk answer"}


@pytest.fixture
def dummy_node_with_pipe():
    """
    Fixture for a GenerateAnswerNode instance using DummyLLMWithPipe.
    Uses a valid input keys string ("dummy_input & doc") to avoid parsing errors.
    """
    node_config = {"llm_model": DummyLLMWithPipe(), "verbose": False, "timeout": 480}
    node = GenerateAnswerNode("dummy_input & doc", ["output"], node_config=node_config)
    node.logger = DummyLogger()
    node.get_input_keys = lambda state: ["dummy_input", "doc"]
    return node


def test_execute_multiple_chunks(dummy_node_with_pipe):
    """
    Test the execute() method for a scenario with multiple document chunks.
    It simulates parallel processing of chunks and then merges them.
    """
    state = {
        "dummy_input": "What is the final answer?",
        "doc": ["Chunk text 1", "Chunk text 2"],
    }

    def fake_invoke_with_timeout(chain, inputs, timeout):
        if isinstance(chain, RunnableParallel):
            return {
                "chunk1": {"content": "answer for chunk 1"},
                "chunk2": {"content": "answer for chunk 2"},
            }
        if "context" in inputs and "question" in inputs:
            return {"content": "merged final answer"}
        return {"content": "single answer"}

    dummy_node_with_pipe.invoke_with_timeout = fake_invoke_with_timeout
    output_state = dummy_node_with_pipe.execute(state)
    assert output_state["output"] == {"content": "merged final answer"}


def test_execute_single_chunk(dummy_node_with_pipe):
    """
    Test the execute() method for a single document chunk.
    """
    state = {"dummy_input": "What is the answer?", "doc": ["Only one chunk text"]}

    def fake_invoke_with_timeout(chain, inputs, timeout):
        if "question" in inputs:
            return {"content": "single-chunk answer"}
        return {"content": "unexpected result"}

    dummy_node_with_pipe.invoke_with_timeout = fake_invoke_with_timeout
    output_state = dummy_node_with_pipe.execute(state)
    assert output_state["output"] == {"content": "single-chunk answer"}


def test_execute_merge_json_decode_error(dummy_node_with_pipe):
    """
    Test that execute() handles a JSONDecodeError in the merge chain properly.
    """
    state = {
        "dummy_input": "What is the final answer?",
        "doc": ["Chunk 1 text", "Chunk 2 text"],
    }

    def fake_invoke_with_timeout(chain, inputs, timeout):
        if isinstance(chain, RunnableParallel):
            return {
                "chunk1": {"content": "answer for chunk 1"},
                "chunk2": {"content": "answer for chunk 2"},
            }
        if "context" in inputs and "question" in inputs:
            raise json.JSONDecodeError("Invalid JSON", "", 0)
        return {"content": "unexpected response"}

    dummy_node_with_pipe.invoke_with_timeout = fake_invoke_with_timeout
    output_state = dummy_node_with_pipe.execute(state)
    assert "error" in output_state["output"]
    assert (
        "Invalid JSON response format during merge" in output_state["output"]["error"]
    )


class DummyChain:
    """A dummy chain for simulating a chain's invoke behavior.
    Returns a successful answer in the expected format."""

    def invoke(self, inputs):
        return {"content": "successful answer"}


@pytest.fixture
def dummy_node_for_process():
    """
    Fixture for creating a GenerateAnswerNode instance for testing the process() method success case.
    """
    node_config = {"llm_model": DummyChain(), "verbose": False, "timeout": 1}
    node = GenerateAnswerNode(
        "user_prompt & content", ["output"], node_config=node_config
    )
    node.logger = DummyLogger()
    node.get_input_keys = lambda state: ["user_prompt", "content"]
    return node


def test_process_success(dummy_node_for_process):
    """
    Test that process() successfully generates an answer when both user prompt and content are provided.
    """
    state = {
        "user_prompt": "What is the answer?",
        "content": "This is some valid context.",
    }
    dummy_node_for_process.chain = DummyChain()
    dummy_node_for_process.invoke_with_timeout = (
        lambda chain, inputs, timeout: chain.invoke(inputs)
    )
    new_state = dummy_node_for_process.process(state)
    assert new_state["output"] == {"content": "successful answer"}


def test_execute_timeout_single_chunk(dummy_node_with_pipe):
    """
    Test that execute() properly handles a Timeout exception in the single chunk branch.
    """
    state = {"dummy_input": "What is the answer?", "doc": ["Only one chunk text"]}

    def fake_invoke_timeout(chain, inputs, timeout):
        raise Timeout("Simulated timeout error")

    dummy_node_with_pipe.invoke_with_timeout = fake_invoke_timeout
    output_state = dummy_node_with_pipe.execute(state)
    assert "error" in output_state["output"]
    assert "Response timeout exceeded" in output_state["output"]["error"]
    assert "Simulated timeout error" in output_state["output"]["raw_response"]


def test_execute_script_creator_single_chunk():
    """
    Test the execute() method for the scenario when script_creator mode is enabled.
    This verifies that the non-markdown prompt templates branch is executed and the expected answer is generated.
    """
    node_config = {
        "llm_model": DummyLLMWithPipe(),
        "verbose": False,
        "timeout": 480,
        "script_creator": True,
        "force": False,
        "is_md_scraper": False,
        "additional_info": "TEST INFO: ",
    }
    node = GenerateAnswerNode("dummy_input & doc", ["output"], node_config=node_config)
    node.logger = DummyLogger()
    node.get_input_keys = lambda state: ["dummy_input", "doc"]
    state = {
        "dummy_input": "What is the script answer?",
        "doc": ["Only one chunk script"],
    }

    def fake_invoke_with_timeout(chain, inputs, timeout):
        if "question" in inputs:
            return {"content": "script single-chunk answer"}
        return {"content": "unexpected response"}

    node.invoke_with_timeout = fake_invoke_with_timeout
    output_state = node.execute(state)
    assert output_state["output"] == {"content": "script single-chunk answer"}


class DummyChatOllama(ChatOllama):
    """A dummy ChatOllama class to simulate ChatOllama behavior."""


class DummySchema:
    """A dummy schema class with a model_json_schema method."""

    def model_json_schema(self):
        return "dummy_schema_json"


def test_init_chat_ollama_format():
    """
    Test that the __init__ method of GenerateAnswerNode sets the format attribute of a ChatOllama LLM correctly.
    """
    dummy_llm = DummyChatOllama()
    node_config = {"llm_model": dummy_llm, "verbose": False, "timeout": 1}
    node = GenerateAnswerNode("dummy_input", ["output"], node_config=node_config)
    assert node.llm_model.format == "json"
    dummy_llm_with_schema = DummyChatOllama()
    node_config_with_schema = {
        "llm_model": dummy_llm_with_schema,
        "verbose": False,
        "timeout": 1,
        "schema": DummySchema(),
    }
    node2 = GenerateAnswerNode(
        "dummy_input", ["output"], node_config=node_config_with_schema
    )
    assert node2.llm_model.format == "dummy_schema_json"
