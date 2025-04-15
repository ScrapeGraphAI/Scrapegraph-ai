from pydantic import BaseModel

from scrapegraphai.graphs.xml_scraper_multi_graph import XMLScraperMultiGraph

XMLScraperMultiGraph._create_llm = lambda self, llm_config: None


# Define a fake graph class to simulate the behavior of the graph.execute() method.
class FakeGraph:
    def __init__(self, final_state):
        self.final_state = final_state

    def execute(self, inputs):
        # Return final_state and dummy execution_info.
        return self.final_state, {"info": "dummy execution info"}


class DummySchema(BaseModel):
    dummy_field: str


class TestXMLScraperMultiGraph:
    """Test suite for XMLScraperMultiGraph"""

    def test_run_returns_answer(self):
        """Test run method returns the expected answer when provided in final state."""
        prompt = "Test prompt"
        source = ["http://example.com"]
        config = {"llm": {"model": "openai/test-model"}}
        graph = XMLScraperMultiGraph(prompt, source, config)
        expected_answer = "Expected Answer"
        # Inject fake graph that returns expected answer
        graph.graph = FakeGraph({"answer": expected_answer})
        result = graph.run()
        assert result == expected_answer

    def test_run_no_answer_found(self):
        """Test run method returns default answer when no answer is present in final state."""
        prompt = "Test prompt"
        source = ["http://example.com"]
        config = {"llm": {"model": "openai/test-model"}}
        graph = XMLScraperMultiGraph(prompt, source, config)
        # Inject fake graph that returns empty final_state
        graph.graph = FakeGraph({})
        result = graph.run()
        assert result == "No answer found."

    def test_create_graph_structure(self):
        """Test that _create_graph produces a graph structure with expected nodes and edges."""
        prompt = "Test prompt"
        source = ["http://example.com"]
        config = {"llm": {"model": "openai/test-model"}, "other_config": "value"}
        dummy_schema = DummySchema
        graph_instance = XMLScraperMultiGraph(prompt, source, config, dummy_schema)
        # Create graph structure using _create_graph
        created_graph = graph_instance._create_graph()
        # Check that the created graph has nodes and edges defined
        assert hasattr(created_graph, "nodes")
        assert hasattr(created_graph, "edges")
        # Check that entry_point is one of the nodes
        assert created_graph.entry_point in created_graph.nodes

    def test_config_and_schema_deepcopy(self):
        """Test that modifying the original config and schema does not affect the instance copies."""
        prompt = "Test prompt"
        source = ["http://example.com"]
        original_config = {"llm": {"model": "openai/test-model"}, "list": [1, 2, 3]}
        original_schema = DummySchema
        graph_instance = XMLScraperMultiGraph(
            prompt, source, original_config, original_schema
        )
        # Modify original config after initialization
        original_config["list"].append(4)
        # The instance copy should remain unchanged
        assert graph_instance.copy_config["list"] == [1, 2, 3]
        # Similarly, for schema, since it's a deepcopy of the reference, it should be equal to original_schema
        assert graph_instance.copy_schema == original_schema
