from unittest.mock import patch, MagicMock
from scrapegraphai.graphs.depth_search_graph import DepthSearchGraph
from scrapegraphai.graphs.abstract_graph import AbstractGraph
import pytest


class TestDepthSearchGraph:
    """Test suite for DepthSearchGraph class"""

    @pytest.mark.parametrize(
        "source, expected_input_key",
        [
            ("https://example.com", "url"),
            ("/path/to/local/directory", "local_dir"),
        ],
    )
    def test_depth_search_graph_initialization(self, source, expected_input_key):
        """
        Test that DepthSearchGraph initializes correctly with different source types.
        This test verifies that the input_key is set to 'url' for web sources and
        'local_dir' for local directory sources.
        """
        prompt = "Test prompt"
        config = {"llm": {"model": "mock_model"}}
        
        # Mock both BaseGraph and _create_llm method
        with patch("scrapegraphai.graphs.depth_search_graph.BaseGraph"), \
             patch.object(AbstractGraph, '_create_llm', return_value=MagicMock()):
            graph = DepthSearchGraph(prompt, source, config)
            
            assert graph.prompt == prompt
            assert graph.source == source
            assert graph.config == config
            assert graph.input_key == expected_input_key
