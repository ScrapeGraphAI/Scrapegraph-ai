"""GenerateAnswerNode returns its error dict when the model reply is not JSON.

The node's chains end in LangChain JSON output parsers, which raise
``OutputParserException`` for a non-JSON reply. These tests run the node with a
fake chat model and the real parsers instead of simulating the exception.
"""

import threading

import pytest
from langchain_core.language_models import FakeListChatModel
from pydantic import BaseModel

from scrapegraphai.nodes.generate_answer_node import GenerateAnswerNode

NOT_JSON = "Sorry, I cannot answer that in JSON."

_reply_lock = threading.Lock()


class OrderedFakeListChatModel(FakeListChatModel):
    """FakeListChatModel that hands out its replies in order even when the chunk
    chains call it from several threads at once."""

    def _call(self, *args, **kwargs):
        with _reply_lock:
            return super()._call(*args, **kwargs)


class Product(BaseModel):
    name: str


def run_node(responses, chunks, schema=None):
    node_config = {"llm_model": OrderedFakeListChatModel(responses=responses)}
    if schema is not None:
        node_config["schema"] = schema
    node = GenerateAnswerNode(
        input="user_prompt & (relevant_chunks | parsed_doc | doc)",
        output=["answer"],
        node_config=node_config,
    )
    state = node.execute({"user_prompt": "What is the product?", "doc": chunks})
    return state["answer"]


def test_single_chunk_non_json_reply_returns_error():
    answer = run_node([NOT_JSON], ["page"])

    assert answer["error"] == "Invalid JSON response format"
    assert NOT_JSON in answer["raw_response"]


def test_single_chunk_non_json_reply_with_schema_returns_error():
    answer = run_node([NOT_JSON], ["page"], schema=Product)

    assert answer["error"] == "Invalid JSON response format"
    assert NOT_JSON in answer["raw_response"]


def test_chunk_stage_non_json_reply_returns_error():
    answer = run_node([NOT_JSON], ["chunk 1", "chunk 2"])

    assert answer["error"] == "Invalid JSON response format in chunk processing"
    assert NOT_JSON in answer["raw_response"]


def test_merge_stage_non_json_reply_returns_error():
    # Both chunk replies are valid JSON, only the merge reply is not.
    answer = run_node(
        ['{"content": "part 1"}', '{"content": "part 2"}', NOT_JSON],
        ["chunk 1", "chunk 2"],
    )

    assert answer["error"] == "Invalid JSON response format during merge"
    assert NOT_JSON in answer["raw_response"]


@pytest.mark.parametrize(
    ("responses", "chunks", "schema", "expected"),
    [
        (['{"content": "Widget"}'], ["page"], None, {"content": "Widget"}),
        (['{"name": "Widget"}'], ["page"], Product, {"name": "Widget"}),
        (
            ['{"content": "part 1"}', '{"content": "part 2"}', '{"content": "Widget"}'],
            ["chunk 1", "chunk 2"],
            None,
            {"content": "Widget"},
        ),
    ],
    ids=["single-chunk", "single-chunk-schema", "chunks-and-merge"],
)
def test_valid_json_reply_is_parsed(responses, chunks, schema, expected):
    assert run_node(responses, chunks, schema) == expected
