import pytest

from scrapegraphai.graphs.base_graph import BaseGraph
from scrapegraphai.graphs.smart_scraper_multi_concat_graph import (
    SmartScraperMultiConcatGraph,
)


class DummyGraph:
    """A dummy graph to simulate the execute() behavior for testing."""

    def __init__(self, answer=None):
        self.answer = answer

    def execute(self, inputs):
        """
        Simulate execution of the graph.
        If answer is None, return an empty state to simulate a missing answer.
        Otherwise return a state with an answer.
        """
        if self.answer is None:
            return ({}, {})
        return ({"answer": self.answer}, {})


class TestSmartScraperMultiConcatGraph:
    """Tests for SmartScraperMultiConcatGraph."""

    @pytest.fixture
    def graph_instance(self):
        """Fixture to create an instance of SmartScraperMultiConcatGraph with default parameters."""
        prompt = "What is test?"
        source = ["http://example.com"]
        config = {"test_config": True, "llm": {"model": "dummy-model"}}
        instance = SmartScraperMultiConcatGraph(prompt, source, config)
        # Manually set llm_model for testing purposes
        instance.llm_model = {"model": "dummy-model"}
        return instance

    def test_run_with_answer(self, graph_instance):
        """Test that run() returns the expected answer when provided by the dummy graph."""
        expected_answer = "This is the merged answer."
        graph_instance.graph = DummyGraph(answer=expected_answer)
        result = graph_instance.run()
        assert result == expected_answer

    def test_run_no_answer(self, graph_instance):
        """Test that run() returns 'No answer found.' when no answer key is present."""
        graph_instance.graph = DummyGraph(answer=None)  # simulate an empty final state
        result = graph_instance.run()
        assert result == "No answer found."

    def test_create_graph_structure(self, graph_instance):
        """Test that _create_graph returns a BaseGraph instance with expected node names and structure."""
        graph = graph_instance._create_graph()
        assert isinstance(graph, BaseGraph)
        # Verify that the entry point is the GraphIteratorNode and graph name is set correctly
        assert graph.entry_point.node_name == "GraphIteratorNode"
        assert graph.graph_name == "SmartScraperMultiConcatGraph"

        # Check all expected node names exist in the graph
        node_names = [node.node_name for node in graph.nodes]
        expected_nodes = [
            "GraphIteratorNode",
            "ConditionalNode",
            "MergeAnswersNode",
            "ConcatNode",
        ]
        for expected in expected_nodes:
            assert expected in node_names

        # Check that ConditionalNode has edges to both MergeAnswersNode and ConcatNode
        edges_from_conditional = [
            edge for edge in graph.edges if edge[0].node_name == "ConditionalNode"
        ]
        targets = [edge[1].node_name for edge in edges_from_conditional]
        assert "MergeAnswersNode" in targets
        assert "ConcatNode" in targets

    def test_conditional_node_config(self, graph_instance):
        """Test that the ConditionalNode is configured with the correct condition and key_name."""
        graph = graph_instance._create_graph()
        cond_nodes = [
            node for node in graph.nodes if node.node_name == "ConditionalNode"
        ]
        assert len(cond_nodes) == 1
        cond_node = cond_nodes[0]
        assert cond_node.node_config.get("condition") == "len(results) > 2"
        assert cond_node.node_config.get("key_name") == "results"
