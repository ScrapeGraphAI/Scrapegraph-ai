from unittest.mock import MagicMock, patch

import pytest

from scrapegraphai.nodes import RobotsNode


@pytest.fixture
def mock_llm_model():
    mock_model = MagicMock()
    mock_model.model = "ollama/llama3"
    return mock_model


@pytest.fixture
def robots_node(mock_llm_model):
    return RobotsNode(
        input="url",
        output=["is_scrapable"],
        node_config={"llm_model": mock_llm_model, "headless": False},
    )


def _patch_chain(return_value):
    """Patch the prompt | llm_model | output_parser chain to return ``return_value``.

    The composed chain's ``invoke`` is what RobotsNode.execute calls; we make it
    return a deterministic list so no real LLM is contacted.
    """
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = return_value
    prompt_patch = patch("scrapegraphai.nodes.robots_node.PromptTemplate")
    loader_patch = patch(
        "scrapegraphai.nodes.robots_node.AsyncChromiumLoader",
        return_value=MagicMock(load=MagicMock(return_value="User-agent: *\nAllow: /")),
    )
    return mock_chain, prompt_patch, loader_patch


def test_robots_node_scrapable(robots_node):
    state = {"url": "https://perinim.github.io/robots.txt"}

    mock_chain, prompt_patch, loader_patch = _patch_chain(["yes"])
    with prompt_patch as mock_prompt, loader_patch:
        mock_prompt.return_value.__or__.return_value.__or__.return_value = mock_chain
        result_state = robots_node.execute(state)

    assert result_state["is_scrapable"] == "yes"


def test_robots_node_not_scrapable(robots_node):
    state = {"url": "https://twitter.com/home"}

    mock_chain, prompt_patch, loader_patch = _patch_chain(["no"])
    # force_scraping is False by default, so a ValueError is expected
    with prompt_patch as mock_prompt, loader_patch:
        mock_prompt.return_value.__or__.return_value.__or__.return_value = mock_chain
        with pytest.raises(ValueError):
            robots_node.execute(state)


def test_robots_node_force_scrapable(robots_node):
    state = {"url": "https://twitter.com/home"}

    # Set force_scraping to True
    robots_node.force_scraping = True

    mock_chain, prompt_patch, loader_patch = _patch_chain(["no"])
    with prompt_patch as mock_prompt, loader_patch:
        mock_prompt.return_value.__or__.return_value.__or__.return_value = mock_chain
        result_state = robots_node.execute(state)

    assert result_state["is_scrapable"] == "no"


if __name__ == "__main__":
    pytest.main()
