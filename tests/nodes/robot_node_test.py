import pytest
from scrapegraphai.models import Ollama
from scrapegraphai.nodes import RobotsNode

@pytest.fixture
def setup():
    """
    Setup
    """
    # ************************************************
    # Define the configuration for the graph
    # ************************************************

    graph_config = {
        "llm": {
            "model_name": "ollama/llama3",  # Modifica il nome dell'attributo da "model_name" a "model"
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
        node_config={"llm_model": llm_model,
                     "headless": False
                     }
    )

    # ************************************************
    # Define the initial state
    # ************************************************

    initial_state = {
        "url": "https://twitter.com/home"
    }

    return robots_node, initial_state

# ************************************************
# Test the node
# ************************************************

def test_robots_node(setup):
    """
    Run the tests
    """
    robots_node, initial_state = setup  # Estrai l'oggetto RobotsNode e lo stato iniziale dalla tupla

    result = robots_node.execute(initial_state)

    assert result is not None
