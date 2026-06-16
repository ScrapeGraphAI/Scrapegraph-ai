"""
Tests for JSONScraperMultiGraph.
"""
import pytest
from scrapegraphai.graphs import JsonScraperMultiGraph


@pytest.fixture
def mock_json_config():
    return {
        "llm": {
            "model": "mock-model",
        },
    }


class TestJsonScraperMultiGraph:
    """Test suite for JsonScraperMultiGraph."""

    def test_initialization(self, mock_json_config):
        """Test that the graph can be initialized with basic config."""
        graph = JsonScraperMultiGraph(
            prompt="Extract data",
            source="[{\"test\": \"data\"}]",
            config=mock_json_config,
        )
        assert graph is not None

    def test_empty_config_raises_error(self):
        """Test that empty config raises appropriate error."""
        with pytest.raises(Exception):
            JsonScraperMultiGraph(
                prompt="Extract data",
                source="[{\"test\": \"data\"}]",
                config={},
            )
