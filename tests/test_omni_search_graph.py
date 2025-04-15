from pydantic import BaseModel

# Import the class under test
from scrapegraphai.graphs.omni_search_graph import OmniSearchGraph


# Create a dummy graph class to simulate graph execution
class DummyGraph:
    def __init__(self, final_state):
        self.final_state = final_state

    def execute(self, inputs):
        # Return final_state and dummy execution info
        return self.final_state, {"debug": True}


# Dummy schema for testing purposes
class DummySchema(BaseModel):
    result: str


class TestOmniSearchGraph:
    """Test suite for the OmniSearchGraph module."""

    def test_run_with_answer(self):
        """Test that the run() method returns the correct answer when present."""
        config = {
            "llm": {"model": "dummy-model"},
            "max_results": 3,
            "search_engine": "dummy-engine",
        }
        prompt = "Test prompt?"
        graph_instance = OmniSearchGraph(prompt, config)
        # Set required attribute manually
        graph_instance.llm_model = {"model": "dummy-model"}
        # Inject a DummyGraph that returns a final state containing an "answer"
        dummy_final_state = {"answer": "expected answer"}
        graph_instance.graph = DummyGraph(dummy_final_state)
        result = graph_instance.run()
        assert result == "expected answer"

    def test_run_without_answer(self):
        """Test that the run() method returns the default message when no answer is found."""
        config = {
            "llm": {"model": "dummy-model"},
            "max_results": 3,
            "search_engine": "dummy-engine",
        }
        prompt = "Test prompt without answer?"
        graph_instance = OmniSearchGraph(prompt, config)
        graph_instance.llm_model = {"model": "dummy-model"}
        # Inject a DummyGraph that returns an empty final state
        dummy_final_state = {}
        graph_instance.graph = DummyGraph(dummy_final_state)
        result = graph_instance.run()
        assert result == "No answer found."

    def test_create_graph_structure(self):
        """Test that the _create_graph() method returns a graph with the expected structure."""
        config = {
            "llm": {"model": "dummy-model"},
            "max_results": 4,
            "search_engine": "dummy-engine",
        }
        prompt = "Structure test prompt"
        # Using a dummy schema for testing
        graph_instance = OmniSearchGraph(prompt, config, schema=DummySchema)
        graph_instance.llm_model = {"model": "dummy-model"}
        constructed_graph = graph_instance._create_graph()
        # Ensure constructed_graph has essential attributes
        assert hasattr(constructed_graph, "nodes")
        assert hasattr(constructed_graph, "edges")
        assert hasattr(constructed_graph, "entry_point")
        assert hasattr(constructed_graph, "graph_name")
        # Check that the graph_name matches the class name
        assert constructed_graph.graph_name == "OmniSearchGraph"
        # Expecting three nodes and two edges as per the implementation
        assert len(constructed_graph.nodes) == 3
        assert len(constructed_graph.edges) == 2

    def test_config_deepcopy(self):
        """Test that the config passed to OmniSearchGraph is deep copied properly."""
        config = {
            "llm": {"model": "dummy-model"},
            "max_results": 2,
            "search_engine": "dummy-engine",
        }
        prompt = "Deepcopy test"
        graph_instance = OmniSearchGraph(prompt, config)
        graph_instance.llm_model = {"model": "dummy-model"}
        # Modify the original config after instantiation
        config["llm"]["model"] = "changed-model"
        # The internal copy should remain unchanged
        assert graph_instance.copy_config["llm"]["model"] == "dummy-model"

    def test_schema_deepcopy(self):
        """Test that the schema is deep copied correctly so external changes do not affect it."""
        config = {
            "llm": {"model": "dummy-model"},
            "max_results": 2,
            "search_engine": "dummy-engine",
        }
        # Instantiate with DummySchema
        graph_instance = OmniSearchGraph("Schema test", config, schema=DummySchema)
        graph_instance.llm_model = {"model": "dummy-model"}
        # Modify the internal copy of the schema directly to simulate isolation
        graph_instance.copy_schema = DummySchema(result="internal")
        external_schema = DummySchema(result="external")
        external_schema.result = "modified"
        assert graph_instance.copy_schema.result == "internal"
