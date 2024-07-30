import pytest
from unittest.mock import MagicMock
from langchain_community.chat_models import ChatOllama
from scrapegraphai.nodes import RobotsNode

@pytest.fixture
def mock_llm_model():
    mock_model = MagicMock()
    mock_model.model = "ollama/llama3"
    mock_model.__call__ = MagicMock(return_value=["yes"])
    return mock_model

@pytest.fixture
def robots_node(mock_llm_model):
    return RobotsNode(
        input="url",
        output=["is_scrapable"],
        node_config={"llm_model": mock_llm_model, "headless": False}
    )

def test_robots_node_scrapable(robots_node):
    state = {
        "url": "https://perinim.github.io/robots.txt"
    }

    # Mocking AsyncChromiumLoader to return a fake robots.txt content
    robots_node.AsyncChromiumLoader = MagicMock(return_value=MagicMock(load=MagicMock(return_value="User-agent: *\nAllow: /")))

    # Execute the node
    result_state, result = robots_node.execute(state)

    # Check the updated state
    assert result_state["is_scrapable"] == "yes"
    assert result == ("is_scrapable", "yes")

def test_robots_node_not_scrapable(robots_node):
    state = {
        "url": "https://twitter.com/home"
    }

    # Mocking AsyncChromiumLoader to return a fake robots.txt content
    robots_node.AsyncChromiumLoader = MagicMock(return_value=MagicMock(load=MagicMock(return_value="User-agent: *\nDisallow: /")))

    # Mock the LLM response to return "no"
    robots_node.llm_model.__call__.return_value = ["no"]

    # Execute the node and expect a ValueError because force_scraping is False by default
    with pytest.raises(ValueError):
        robots_node.execute(state)

def test_robots_node_force_scrapable(robots_node):
    state = {
        "url": "https://twitter.com/home"
    }

    # Mocking AsyncChromiumLoader to return a fake robots.txt content
    robots_node.AsyncChromiumLoader = MagicMock(return_value=MagicMock(load=MagicMock(return_value="User-agent: *\nDisallow: /")))

    # Mock the LLM response to return "no"
    robots_node.llm_model.__call__.return_value = ["no"]

    # Set force_scraping to True
    robots_node.force_scraping = True

    # Execute the node
    result_state, result = robots_node.execute(state)

    # Check the updated state
    assert result_state["is_scrapable"] == "no"
    assert result == ("is_scrapable", "no")

if __name__ == "__main__":
    pytest.main()
