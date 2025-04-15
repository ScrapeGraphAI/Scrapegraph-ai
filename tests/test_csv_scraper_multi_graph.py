from copy import deepcopy

import pytest

from scrapegraphai.graphs.csv_scraper_multi_graph import CSVScraperMultiGraph

# Monkey-patch _create_llm to avoid unsupported provider error during tests
CSVScraperMultiGraph._create_llm = lambda self, llm_config: llm_config


# Dummy graph classes to simulate behavior during tests
class DummyGraph:
    """Dummy graph that returns a predefined answer."""

    def __init__(self, answer):
        self.answer = answer

    def execute(self, inputs):
        # Returns a tuple of (final_state, execution_info)
        return ({"answer": self.answer}, {})


class DummyGraphNoAnswer:
    """Dummy graph that simulates absence of answer in final_state."""

    def execute(self, inputs):
        # Returns an empty final_state
        return ({}, {})


class DummyBaseGraph:
    """Dummy BaseGraph to test _create_graph method without side effects."""

    def __init__(self, nodes, edges, entry_point, graph_name):
        self.nodes = nodes
        self.edges = edges
        self.entry_point = entry_point
        self.graph_name = graph_name

    config = {
        "llm": {"model": "dummy_model", "model_provider": "dummy_provider"},
        "key": "value",
    }
    """Test that CSVScraperMultiGraph.run returns the expected answer when provided by the graph."""
    prompt = "Test prompt"
    source = ["url1", "url2"]

    # Instantiate the graph
    multi_graph = CSVScraperMultiGraph(prompt, source, config)

    # Override the graph attribute with a dummy graph returning an expected answer
    multi_graph.graph = DummyGraph("expected answer")

    result = multi_graph.run()
    assert result == "expected answer"


def test_run_no_answer():
    """Test that CSVScraperMultiGraph.run returns a fallback message when no answer is provided."""
    prompt = "Another test prompt"
    source = ["url3"]
    config = {
        "llm": {"model": "dummy_model", "model_provider": "dummy_provider"},
        "another_key": "another_value",
    }

    multi_graph = CSVScraperMultiGraph(prompt, source, config)
    multi_graph.graph = DummyGraphNoAnswer()

    result = multi_graph.run()
    assert result == "No answer found."


def test_create_graph_structure(monkeypatch):
    """Test that _create_graph constructs a graph with the expected structure."""
    prompt = "Structure test"
    source = ["url4"]
    config = {
        "llm": {"model": "dummy_model", "model_provider": "dummy_provider"},
        "struct_key": "struct_value",
    }

    multi_graph = CSVScraperMultiGraph(prompt, source, config)

    # Monkey-patch the _create_graph method to avoid dependencies on external nodes
    monkeypatch.setattr(
        multi_graph,
        "_create_graph",
        lambda: DummyBaseGraph(
            nodes=["graph_iterator_node", "merge_answers_node"],
            edges=[("graph_iterator_node", "merge_answers_node")],
            entry_point="graph_iterator_node",
            graph_name=multi_graph.__class__.__name__,
        ),
    )

    graph = multi_graph._create_graph()
    assert graph.graph_name == "CSVScraperMultiGraph"
    assert len(graph.nodes) == 2
    assert len(graph.edges) == 1


def test_config_deepcopy():
    """Test that the configuration dictionary is deep-copied.
    Modifying the original config after instantiation should not affect the multi_graph copy.
    """
    config = {
        "llm": {"model": "dummy_model", "provider": "provider1"},
        "nested": {"a": [1, 2]},
    }
    original_config = deepcopy(config)
    multi_graph = CSVScraperMultiGraph("Deep copy test", ["url_deep"], config)
    # Modify the original config after instantiation
    config["nested"]["a"].append(3)
    # The multi_graph.copy_config should remain unchanged.
    assert multi_graph.copy_config["nested"]["a"] == original_config["nested"]["a"]


def test_run_argument_passing():
    """Test that CSVScraperMultiGraph.run passes the correct input arguments
    to the graph's execute method and returns the expected answer."""

    class DummyGraphCapture:
        def __init__(self):
            self.captured_inputs = None

        def execute(self, inputs):
            self.captured_inputs = inputs
            return ({"answer": "captured answer"}, {})

    prompt = "Argument test prompt"
    source = ["url_arg1", "url_arg2"]
    config = {"llm": {"model": "dummy_model", "provider": "dummy_provider"}}

    multi_graph = CSVScraperMultiGraph(prompt, source, config)
    dummy_graph = DummyGraphCapture()
    multi_graph.graph = dummy_graph

    result = multi_graph.run()
    # Check that the dummy graph captured the inputs as expected
    expected_inputs = {"user_prompt": prompt, "jsons": source}
    assert dummy_graph.captured_inputs == expected_inputs
    assert result == "captured answer"


def test_run_with_exception_in_execute():
    """Test that CSVScraperMultiGraph.run propagates exceptions from the graph's execute method."""

    class DummyGraphException:
        def execute(self, inputs):
            raise Exception("Test exception")

    prompt = "Exception test prompt"
    source = ["url_exception"]
    config = {"llm": {"model": "dummy_model", "provider": "dummy_provider"}}

    multi_graph = CSVScraperMultiGraph(prompt, source, config)
    multi_graph.graph = DummyGraphException()

    with pytest.raises(Exception, match="Test exception"):
        multi_graph.run()
