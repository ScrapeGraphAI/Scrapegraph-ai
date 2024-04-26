"""
Module for testinh robot_node
"""
import os
from dotenv import load_dotenv
import pytest
from scrapegraphai.models import OpenAI
from scrapegraphai.nodes import RobotsNode

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def setup():
    """
    setup
    """
    # ************************************************
    # Define the configuration for the graph
    # ************************************************

    openai_key = os.getenv("OPENAI_APIKEY")

    graph_config = {
        "llm": {
            "api_key": openai_key,
            "model": "gpt-3.5-turbo",
            "temperature": 0,
            "streaming": True
        },
    }

    # ************************************************
    # Define the node
    # ************************************************

    llm_model = OpenAI(graph_config["llm"])

    robots_node = RobotsNode(
        input="url",
        output=["is_scrapable"],
        node_config={"llm": llm_model}
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
