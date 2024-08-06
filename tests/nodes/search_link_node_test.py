import pytest
from langchain_community.chat_models import ChatOllama
from scrapegraphai.nodes import SearchLinkNode
from unittest.mock import patch, MagicMock

@pytest.fixture
def setup():
    """
    Setup the SearchLinkNode and initial state for testing.
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
    llm_model = ChatOllama(graph_config["llm"])

    # Define the SearchLinkNode with necessary configurations
    search_link_node = SearchLinkNode(
        input=["user_prompt", "parsed_content_chunks"],
        output=["relevant_links"],
        node_config={
            "llm_model": llm_model,
            "verbose": False
        }
    )

    # Define the initial state for the node
    initial_state = {
        "user_prompt": "Example user prompt",
        "parsed_content_chunks": [
            {"page_content": "Example page content 1"},
            {"page_content": "Example page content 2"},
            # Add more example page content dictionaries as needed
        ]
    }

    return search_link_node, initial_state

def test_search_link_node(setup):
    """
    Test the SearchLinkNode execution.
    """
    search_link_node, initial_state = setup

    # Patch the execute method to avoid actual network calls and return a mock response
    with patch.object(SearchLinkNode, 'execute', return_value={"relevant_links": ["http://example.com"]}) as mock_execute:
        result = search_link_node.execute(initial_state)

        # Check if the result is not None
        assert result is not None
        # Additional assertion to check the returned value
        assert "relevant_links" in result
        assert isinstance(result["relevant_links"], list)
        assert len(result["relevant_links"]) > 0
        # Ensure the execute method was called once
        mock_execute.assert_called_once_with(initial_state)
