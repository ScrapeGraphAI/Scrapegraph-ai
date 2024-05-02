"""
Module for testinh robot_node
"""
import pytest
from scrapegraphai.models import Ollama
from scrapegraphai.nodes import RobotsNode


@pytest.fixture
def setup():
    """
    setup
    """
    # ************************************************
    # Define the configuration for the graph
    # ************************************************

    graph_config = {
        "llm": {
            "model": "ollama/llama3",
            "temperature": 0,
            "streaming": True
        },
    }

    # ************************************************
    # Define the node
    # ************************************************

    llm_model = Ollama(graph_config["llm"])

    robots_node = RobotsNode(
        input="url",
        output=["is_scrapable"],
        node_config={"llm": llm_model,
                     "headless": False
                     }
    )

    return robots_node

# ************************************************
# Test the node
# ************************************************


def test_robots_node(setup):
    """
    Run the tests
    """
    state = {
        "url": "https://twitter.com/home"
    }

    result = setup.execute(state)

    assert result is not None


# If you need to run this script directly
if __name__ == "__main__":
    pytest.main()
