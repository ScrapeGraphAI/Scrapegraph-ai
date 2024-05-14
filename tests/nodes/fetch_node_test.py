"""
Module for testinh fetch_node
"""
import pytest
from scrapegraphai.nodes import FetchNode


@pytest.fixture
def setup():
    """
    setup
    """
    # ************************************************
    # Define the node
    # ************************************************

    fetch_node = FetchNode(
        input="url | local_dir",
        output=["doc"],
        node_config={
            "headless": False
        }
    )

    return fetch_node

# ************************************************
# Test the node
# ************************************************


def test_fetch_node(setup):
    """
    Run the tests
    """
    state = {
        "url": "https://twitter.com/home"
    }

    result = setup.execute(state)

    assert result is not None
