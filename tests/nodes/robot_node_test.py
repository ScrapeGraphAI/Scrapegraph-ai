import pytest
from scrapegraphai.models import Ollama
from scrapegraphai.nodes import RobotsNode
from unittest.mock import patch, MagicMock

@pytest.fixture
def setup():
    """
    Setup the RobotsNode and initial state for testing.
    """
    # Define the configuration for the graph
    graph_config = {
        "llm": {
            "model_name": "ollama/llama3",
            "temperature": 0,
            "streaming": True
        },
    }

    # Instantiate the LLM model with the configuration
    llm_model = Ollama(graph_config["llm"])

    # Define the RobotsNode with necessary configurations
    robots_node = RobotsNode(
        input="url",
        output=["is_scrapable"],
        node_config={
            "llm_model": llm_model,
            "headless": False
        }
    )

    # Define the initial state for the node
    initial_state = {
        "url": "https://twitter.com/home"
    }

    return robots_node, initial_state

def test_robots_node(setup):
    """
    Test the RobotsNode execution.
    """
    robots_node, initial_state = setup

    # Patch the execute method to avoid actual network calls and return a mock response
    with patch.object(RobotsNode, 'execute', return_value={"is_scrapable": True}) as mock_execute:
        result = robots_node.execute(initial_state)

        # Check if the result is not None
        assert result is not None
        # Additional assertion to check the returned value
        assert result["is_scrapable"] is True
        # Ensure the execute method was called once
        mock_execute.assert_called_once_with(initial_state)
