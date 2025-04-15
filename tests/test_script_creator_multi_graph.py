import pytest
from pydantic import BaseModel

from scrapegraphai.graphs.script_creator_graph import ScriptCreatorGraph
from scrapegraphai.graphs.script_creator_multi_graph import (
    BaseGraph,
    ScriptCreatorMultiGraph,
)


@pytest.fixture(autouse=True)
def set_api_key_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "dummy")


# Dummy classes to simulate behavior for testing
class DummyGraph:
    def __init__(self, final_state, execution_info):
        self.final_state = final_state
        self.execution_info = execution_info

    def execute(self, inputs):
        return self.final_state, self.execution_info


class DummySchema(BaseModel):
    field: str = "dummy"


class TestScriptCreatorMultiGraph:
    """Tests for ScriptCreatorMultiGraph."""

    def test_run_success(self):
        """Test run() returns the merged script when execution is successful."""
        prompt = "Test prompt"
        source = ["http://example.com"]
        config = {"llm": {"model": "openai/test-model"}}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        # Set necessary attributes that are expected by _create_graph() and the run() method.
        instance.llm_model = {"model": "openai/test-model"}
        instance.schema = {"type": "dummy"}
        # Replace the graph with a dummy graph that simulates successful execution.
        dummy_final_state = {"merged_script": "print('Hello World')"}
        dummy_execution_info = {"info": "dummy"}
        instance.graph = DummyGraph(dummy_final_state, dummy_execution_info)
        result = instance.run()
        assert result == "print('Hello World')"

    def test_run_failure(self):
        """Test run() returns failure message when merged_script is missing."""
        prompt = "Test prompt"
        source = ["http://example.com"]
        config = {"llm": {"model": "openai/test-model"}}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        instance.llm_model = {"model": "openai/test-model"}
        instance.schema = {"type": "dummy"}
        dummy_final_state = {"other_key": "no script"}
        dummy_execution_info = {"info": "dummy"}
        instance.graph = DummyGraph(dummy_final_state, dummy_execution_info)
        result = instance.run()
        assert result == "Failed to generate the script."

    def test_create_graph_structure(self):
        """Test _create_graph() returns a BaseGraph with the correct graph name and structure."""
        prompt = "Test prompt"
        source = []
        config = {"llm": {"model": "openai/test-model"}}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        # Manually assign llm_model and schema for node configuration in the graph.
        instance.llm_model = {"model": "openai/test-model"}
        instance.schema = {"type": "dummy"}
        graph = instance._create_graph()
        assert isinstance(graph, BaseGraph)
        assert hasattr(graph, "graph_name")
        assert graph.graph_name == "ScriptCreatorMultiGraph"
        # Check that the graph has two nodes.
        assert len(graph.nodes) == 2
        # Optional: Check that the edges list is correctly formed.
        assert len(graph.edges) == 1

    def test_config_deepcopy(self):
        """Test that the configuration is deep copied during initialization."""
        prompt = "Test prompt"
        source = []
        config = {"llm": {"model": "openai/test-model"}, "other": [1, 2, 3]}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        # Modify the original config.
        config["llm"]["model"] = "changed-model"
        config["other"].append(4)
        # Verify that the config copied within instance remains unchanged.
        assert instance.copy_config["llm"]["model"] == "openai/test-model"
        assert instance.copy_config["other"] == [1, 2, 3]

    def test_init_attributes(self):
        """Test that initial attributes are set correctly upon initialization."""
        prompt = "Initialization test"
        source = ["http://init.com"]
        config = {"llm": {"model": "openai/init-model"}, "param": [1, 2]}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        # Check that basic attributes are set correctly
        assert instance.prompt == prompt
        assert instance.source == source
        # Check that copy_config is a deep copy and equals the original config
        assert instance.copy_config == {
            "llm": {"model": "openai/init-model"},
            "param": [1, 2],
        }
        # For classes, deepcopy returns the same object, so the copy_schema should equal schema
        assert instance.copy_schema == DummySchema

    def test_run_no_schema(self):
        """Test run() when schema is None."""
        prompt = "No schema prompt"
        source = ["http://noschema.com"]
        config = {"llm": {"model": "openai/no-schema"}}
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema=None)
        instance.llm_model = {"model": "openai/no-schema"}
        instance.schema = None
        dummy_final_state = {"merged_script": "print('No Schema Script')"}
        dummy_execution_info = {"info": "no schema"}
        instance.graph = DummyGraph(dummy_final_state, dummy_execution_info)
        result = instance.run()
        assert result == "print('No Schema Script')"

    def test_create_graph_node_configs(self):
        """Test that _create_graph() sets correct node configurations for its nodes."""
        prompt = "Graph config test"
        source = ["http://graphconfig.com"]
        config = {"llm": {"model": "openai/graph-model"}, "extra": [10]}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        # Manually assign llm_model and schema for node configuration
        instance.llm_model = {"model": "openai/graph-model"}
        instance.schema = {"type": "graph-dummy"}
        graph = instance._create_graph()
        # Validate configuration of the first node (GraphIteratorNode)
        node1 = graph.nodes[0]
        assert node1.node_config["graph_instance"] == ScriptCreatorGraph
        assert node1.node_config["scraper_config"] == instance.copy_config
        # Validate configuration of the second node (MergeGeneratedScriptsNode)
        node2 = graph.nodes[1]
        assert node2.node_config["llm_model"] == instance.llm_model
        assert node2.node_config["schema"] == instance.schema

    def test_entry_point_node(self):
        """Test that the graph entry point is the GraphIteratorNode (the first node)."""
        prompt = "Entry point test"
        source = ["http://entrypoint.com"]
        config = {"llm": {"model": "openai/test-model"}}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        instance.llm_model = {"model": "openai/test-model"}
        instance.schema = {"type": "dummy"}
        graph = instance._create_graph()
        assert graph.entry_point == graph.nodes[0]

    def test_run_exception(self):
        """Test that run() propagates exceptions raised by graph.execute."""
        prompt = "Exception test"
        source = ["http://exception.com"]
        config = {"llm": {"model": "openai/test-model"}}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        instance.llm_model = {"model": "openai/test-model"}
        instance.schema = {"type": "dummy"}

        # Create a dummy graph that raises an exception when execute is called.
        class ExceptionGraph:
            def execute(self, inputs):
                raise ValueError("Testing exception")

        instance.graph = ExceptionGraph()
        with pytest.raises(ValueError, match="Testing exception"):
            instance.run()

    def test_run_with_empty_prompt(self):
        """Test run() method with an empty prompt."""
        prompt = ""
        source = ["http://emptyprompt.com"]
        config = {"llm": {"model": "openai/test-model"}}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        instance.llm_model = {"model": "openai/test-model"}
        instance.schema = {"type": "dummy"}
        dummy_final_state = {"merged_script": "print('Empty prompt')"}
        dummy_execution_info = {"info": "empty prompt"}
        instance.graph = DummyGraph(dummy_final_state, dummy_execution_info)
        result = instance.run()
        assert result == "print('Empty prompt')"

    def test_run_called_twice(self):
        """Test that running run() twice returns consistent and updated results."""
        prompt = "Twice test"
        source = ["http://twicetest.com"]
        config = {"llm": {"model": "openai/test-model"}}
        schema = DummySchema
        instance = ScriptCreatorMultiGraph(prompt, source, config, schema)
        instance.llm_model = {"model": "openai/test-model"}
        instance.schema = {"type": "dummy"}
        dummy_final_state = {"merged_script": "print('First run')"}
        dummy_execution_info = {"info": "first run"}
        dummy_graph = DummyGraph(dummy_final_state, dummy_execution_info)
        instance.graph = dummy_graph
        result1 = instance.run()
        # Modify dummy graph's state for the second run.
        dummy_graph.final_state["merged_script"] = "print('Second run')"
        dummy_graph.execution_info = {"info": "second run"}
        result2 = instance.run()
        assert result1 == "print('First run')"
        assert result2 == "print('Second run')"
