"""
Module for testinh robot_node
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

    robots_node = FetchNode(
        input="url | local_dir",
        output=["doc"],
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
