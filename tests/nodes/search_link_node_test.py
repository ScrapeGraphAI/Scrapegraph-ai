import pytest
from scrapegraphai.models import Ollama
from scrapegraphai.nodes import SearchLinkNode

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

    search_link_node = SearchLinkNode(
        input=["user_prompt", "parsed_content_chunks"],
        output=["relevant_links"],
        node_config={"llm_model": llm_model,
                     "verbose": False
                     }
    )

    # ************************************************
    # Define the initial state
    # ************************************************

    initial_state = {
        "user_prompt": "Example user prompt",
        "parsed_content_chunks": [
            {"page_content": "Example page content 1"},
            {"page_content": "Example page content 2"},
            # Add more example page content dictionaries as needed
        ]
    }

    return search_link_node, initial_state

# ************************************************
# Test the node
# ************************************************

def test_search_link_node(setup):
    """
    Run the tests
    """
    search_link_node, initial_state = setup  # Extract the SearchLinkNode object and the initial state from the tuple

    result = search_link_node.execute(initial_state)

    # Assert that the result is not None
    assert result is not None
