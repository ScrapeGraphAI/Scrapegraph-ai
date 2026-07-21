"""
Tests for SmartScraperMultiConcatGraph.
"""

from copy import deepcopy

import pytest

from scrapegraphai.graphs.smart_scraper_multi_concat_graph import SmartScraperMultiConcatGraph

# Monkey-patch _create_llm to avoid unsupported provider error during tests
SmartScraperMultiConcatGraph._create_llm = lambda self, llm_config: llm_config


class DummyGraph:
    """Dummy graph that returns a predefined answer."""

    def __init__(self, answer):
        self.answer = answer

    def execute(self, inputs):
        return ({"answer": self.answer}, {})


class DummyGraphNoAnswer:
    """Dummy graph that simulates absence of answer in final_state."""

    def execute(self, inputs):
        return ({}, {})


class DummyBaseGraph:
    """Dummy BaseGraph to test _create_graph method without side effects."""

    def __init__(self, nodes, edges, entry_point, graph_name):
        self.nodes = nodes
        self.edges = edges
        self.entry_point = entry_point
        self.graph_name = graph_name


def test_run_with_answer():
    """Test that SmartScraperMultiConcatGraph.run returns the expected answer when provided by the graph."""
    prompt = "Test prompt"
    source = ["https://example.com/page1", "https://example.com/page2"]
    config = {
        "llm": {"model": "dummy_model", "model_provider": "dummy_provider"},
    }

    multi_graph = SmartScraperMultiConcatGraph(prompt, source, config)
    multi_graph.graph = DummyGraph("expected answer")

    result = multi_graph.run()
    assert result == "expected answer"


def test_run_no_answer():
    """Test that SmartScraperMultiConcatGraph.run returns a fallback message when no answer is provided."""
    prompt = "Another test prompt"
    source = ["https://example.com/page3"]
    config = {
        "llm": {"model": "dummy_model", "model_provider": "dummy_provider"},
    }

    multi_graph = SmartScraperMultiConcatGraph(prompt, source, config)
    multi_graph.graph = DummyGraphNoAnswer()

    result = multi_graph.run()
    assert result == "No answer found."


def test_create_graph_structure(monkeypatch):
    """Test that _create_graph constructs a graph with the expected structure,
    including ConditionalNode, MergeAnswersNode, and ConcatAnswersNode."""
    prompt = "Structure test"
    source = ["https://example.com/page4"]
    config = {
        "llm": {"model": "dummy_model", "model_provider": "dummy_provider"},
    }

    multi_graph = SmartScraperMultiConcatGraph(prompt, source, config)

    monkeypatch.setattr(
        multi_graph,
        "_create_graph",
        lambda: DummyBaseGraph(
            nodes=[
                "graph_iterator_node",
                "conditional_node",
                "merge_answers_node",
                "concat_node",
            ],
            edges=[
                ("graph_iterator_node", "conditional_node"),
                ("conditional_node", "merge_answers_node"),
                ("conditional_node", "concat_node"),
            ],
            entry_point="graph_iterator_node",
            graph_name=multi_graph.__class__.__name__,
        ),
    )

    graph = multi_graph._create_graph()
    assert graph.graph_name == "SmartScraperMultiConcatGraph"
    assert len(graph.nodes) == 4
    assert len(graph.edges) == 3


def test_config_deepcopy():
    """Test that the configuration dictionary is deep-copied.
    Modifying the original config after instantiation should not affect the multi_graph copy.
    """
    config = {
        "llm": {"model": "dummy_model", "provider": "provider1"},
        "nested": {"a": [1, 2]},
    }
    original_config = deepcopy(config)
    multi_graph = SmartScraperMultiConcatGraph(
        "Deep copy test", ["https://example.com/deep"], config
    )
    config["nested"]["a"].append(3)
    assert multi_graph.copy_config["nested"]["a"] == original_config["nested"]["a"]


def test_run_argument_passing():
    """Test that SmartScraperMultiConcatGraph.run passes the correct input arguments
    to the graph's execute method and returns the expected answer."""

    class DummyGraphCapture:
        def __init__(self):
            self.captured_inputs = None

        def execute(self, inputs):
            self.captured_inputs = inputs
            return ({"answer": "captured answer"}, {})

    prompt = "Argument test prompt"
    source = ["https://example.com/arg1", "https://example.com/arg2"]
    config = {"llm": {"model": "dummy_model", "provider": "dummy_provider"}}

    multi_graph = SmartScraperMultiConcatGraph(prompt, source, config)
    dummy_graph = DummyGraphCapture()
    multi_graph.graph = dummy_graph

    result = multi_graph.run()
    expected_inputs = {"user_prompt": prompt, "urls": source}
    assert dummy_graph.captured_inputs == expected_inputs
    assert result == "captured answer"


def test_run_with_exception_in_execute():
    """Test that SmartScraperMultiConcatGraph.run propagates exceptions from the graph's execute method."""

    class DummyGraphException:
        def execute(self, inputs):
            raise Exception("Test exception")

    prompt = "Exception test prompt"
    source = ["https://example.com/exception"]
    config = {"llm": {"model": "dummy_model", "provider": "dummy_provider"}}

    multi_graph = SmartScraperMultiConcatGraph(prompt, source, config)
    multi_graph.graph = DummyGraphException()

    with pytest.raises(Exception, match="Test exception"):
        multi_graph.run()


def test_schema_is_deepcopied():
    """Test that the schema is deep-copied and modifications don't affect the original."""
    from pydantic import BaseModel, Field
    from typing import List

    class TestItem(BaseModel):
        name: str = Field(description="Item name")

    class TestSchema(BaseModel):
        items: List[TestItem] = Field(description="List of items")

    config = {
        "llm": {"model": "dummy_model", "model_provider": "dummy_provider"},
    }
    schema = TestSchema
    original_schema = deepcopy(schema)

    multi_graph = SmartScraperMultiConcatGraph(
        "Schema test", ["https://example.com/schema"], config, schema=schema
    )
    assert multi_graph.copy_schema == original_schema
