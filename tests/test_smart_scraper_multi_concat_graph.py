"""
Tests for SmartScraperMultiConcatGraph.
"""
import pytest
from scrapegraphai.graphs import SmartScraperMultiConcatGraph


@pytest.fixture
def mock_concat_config():
    return {
        "llm": {
            "model": "mock-model",
        },
    }


class TestSmartScraperMultiConcatGraph:
    """Test suite for SmartScraperMultiConcatGraph."""

    def test_initialization(self, mock_concat_config):
        """Test that the graph can be initialized with basic config."""
        graph = SmartScraperMultiConcatGraph(
            prompt="Extract data",
            source=["https://example.com"],
            config=mock_concat_config,
        )
        assert graph is not None

    def test_empty_sources_raises_error(self, mock_concat_config):
        """Test that empty sources list raises appropriate error."""
        with pytest.raises(Exception):
            SmartScraperMultiConcatGraph(
                prompt="Extract data",
                source=[],
                config=mock_concat_config,
            )
