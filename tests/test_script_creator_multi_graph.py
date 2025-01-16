import pytest

from copy import deepcopy
from pydantic import BaseModel
from scrapegraphai.graphs.base_graph import BaseGraph
from scrapegraphai.graphs.script_creator_multi_graph import ScriptCreatorMultiGraph
from unittest.mock import AsyncMock, MagicMock, patch

class TestScriptCreatorMultiGraph:
    @pytest.mark.asyncio
    @patch('scrapegraphai.graphs.script_creator_multi_graph.GraphIteratorNode')
    @patch('scrapegraphai.graphs.script_creator_multi_graph.MergeGeneratedScriptsNode')
    async def test_run_with_empty_source(self, mock_merge_node, mock_iterator_node):
        """
        Test the ScriptCreatorMultiGraph.run() method with an empty source list.
        This test checks if the graph handles the case when no URLs are provided.
        """
        # Arrange
        prompt = "What is Chioggia famous for?"
        source = []
        config = {"llm": {"model": "openai/gpt-3.5-turbo"}}

        # Mock the execute method of BaseGraph to return a predefined state
        mock_state = {"merged_script": "No URLs provided, unable to generate script."}
        with patch('scrapegraphai.graphs.script_creator_multi_graph.BaseGraph.execute', return_value=(mock_state, {})):
            graph = ScriptCreatorMultiGraph(prompt, source, config)

            # Act
            result = graph.run()

            # Assert
            assert result == "No URLs provided, unable to generate script."
            assert mock_iterator_node.call_count == 1
            assert mock_merge_node.call_count == 1

    @pytest.mark.asyncio
    @patch('scrapegraphai.graphs.script_creator_multi_graph.GraphIteratorNode')
    @patch('scrapegraphai.graphs.script_creator_multi_graph.MergeGeneratedScriptsNode')
    @patch('scrapegraphai.graphs.script_creator_multi_graph.BaseGraph.execute')
    async def test_run_with_multiple_urls(self, mock_execute, mock_merge_node, mock_iterator_node):
        """
        Test the ScriptCreatorMultiGraph.run() method with multiple URLs in the source list.
        This test checks if the graph correctly processes multiple URLs and generates a merged script.
        """
        # Arrange
        prompt = "What are the main attractions in Venice and Chioggia?"
        source = ["https://example.com/venice", "https://example.com/chioggia"]
        config = {"llm": {"model": "openai/gpt-3.5-turbo"}}

        mock_state = {"merged_script": "Generated script for Venice and Chioggia attractions"}
        mock_execute.return_value = (mock_state, {})

        graph = ScriptCreatorMultiGraph(prompt, source, config)

        # Act
        result = graph.run()

        # Assert
        assert result == "Generated script for Venice and Chioggia attractions"
        mock_execute.assert_called_once()
        mock_iterator_node.assert_called_once()
        mock_merge_node.assert_called_once()

        # Check if the correct inputs were passed to the execute method
        expected_inputs = {"user_prompt": prompt, "urls": source}
        actual_inputs = mock_execute.call_args[0][0]
        assert actual_inputs == expected_inputs

    @pytest.mark.asyncio
    @patch('scrapegraphai.graphs.script_creator_multi_graph.BaseGraph')
    async def test_invalid_llm_configuration(self, mock_base_graph):
        """
        Test the ScriptCreatorMultiGraph initialization with an invalid LLM configuration.
        This test checks if the graph raises a ValueError when an unsupported LLM model is provided.
        """
        # Arrange
        prompt = "What is Chioggia famous for?"
        source = ["https://example.com/chioggia"]
        invalid_config = {"llm": {"model": "unsupported_model"}}

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported LLM model"):
            ScriptCreatorMultiGraph(prompt, source, invalid_config)

        # Ensure that BaseGraph was not instantiated due to the invalid configuration
        mock_base_graph.assert_not_called()

    @pytest.mark.asyncio
    @patch('scrapegraphai.graphs.script_creator_multi_graph.BaseGraph.execute')
    async def test_run_with_execution_failure(self, mock_execute: BaseGraph.execute):
        """
        Test the ScriptCreatorMultiGraph.run() method when graph execution fails.
        This test checks if the method handles the failure gracefully and returns an error message.
        """
        # Arrange
        prompt = "What is Chioggia famous for?"
        source = ["https://example.com/chioggia"]
        config = {"llm": {"model": "openai/gpt-3.5-turbo"}}

        # Simulate a failure in graph execution
        mock_execute.side_effect = Exception("Graph execution failed")

        graph = ScriptCreatorMultiGraph(prompt, source, config)

        # Act
        result = graph.run()

        # Assert
        assert result == "Failed to generate the script."
        mock_execute.assert_called_once()

        # Check if the correct inputs were passed to the execute method
        expected_inputs = {"user_prompt": prompt, "urls": source}
        actual_inputs = mock_execute.call_args[0][0]
        assert actual_inputs == expected_inputs

    @pytest.mark.asyncio
    @patch('scrapegraphai.graphs.script_creator_multi_graph.GraphIteratorNode')
    async def test_custom_schema_passed_to_graph_iterator(self, mock_graph_iterator_node):
        """
        Test that a custom schema is correctly passed to the GraphIteratorNode
        when initializing ScriptCreatorMultiGraph.
        """
        # Arrange
        class CustomSchema(BaseModel):
            title: str
            content: str

        prompt = "What is Chioggia famous for?"
        source = ["https://example.com/chioggia"]
        config = {"llm": {"model": "openai/gpt-3.5-turbo"}}

        # Act
        graph = ScriptCreatorMultiGraph(prompt, source, config, schema=CustomSchema)

        # Assert
        mock_graph_iterator_node.assert_called_once()
        _, kwargs = mock_graph_iterator_node.call_args
        assert kwargs['schema'] == CustomSchema
        assert isinstance(graph.copy_schema, type(CustomSchema))

    @pytest.mark.asyncio
    async def test_config_and_schema_deep_copy(self):
        """
        Test that the config and schema are properly deep copied during initialization
        of ScriptCreatorMultiGraph. This ensures that modifications to the original
        config or schema don't affect the internal state of the ScriptCreatorMultiGraph instance.
        """
        # Arrange
        class CustomSchema(BaseModel):
            title: str
            content: str

        prompt = "What is Chioggia famous for?"
        source = ["https://example.com/chioggia"]
        config = {"llm": {"model": "openai/gpt-3.5-turbo"}, "custom_key": {"nested": "value"}}
        schema = CustomSchema

        # Act
        graph = ScriptCreatorMultiGraph(prompt, source, config, schema=schema)

        # Assert
        assert graph.copy_config == config
        assert graph.copy_config is not config
        assert graph.copy_schema == schema
        assert graph.copy_schema is not schema

        # Modify original config and schema
        config["custom_key"]["nested"] = "modified"
        schema.update_forward_refs()

        # Check that the copied versions remain unchanged
        assert graph.copy_config["custom_key"]["nested"] == "value"
        assert not hasattr(graph.copy_schema, "update_forward_refs")

    @pytest.mark.asyncio
    @patch('scrapegraphai.graphs.script_creator_multi_graph.BaseGraph.execute')
    async def test_run_with_merge_failure(self, mock_execute):
        """
        Test the ScriptCreatorMultiGraph.run() method when the MergeGeneratedScriptsNode fails to merge scripts.
        This test checks if the method handles the failure gracefully and returns an error message
        when the merged_script is not present in the final state.
        """
        # Arrange
        prompt = "What is Chioggia famous for?"
        source = ["https://example.com/chioggia"]
        config = {"llm": {"model": "openai/gpt-3.5-turbo"}}

        # Simulate a failure in merging scripts by returning a state without 'merged_script'
        mock_execute.return_value = ({"some_other_key": "value"}, {})

        graph = ScriptCreatorMultiGraph(prompt, source, config)

        # Act
        result = graph.run()

        # Assert
        assert result == "Failed to generate the script."
        mock_execute.assert_called_once()

        # Check if the correct inputs were passed to the execute method
        expected_inputs = {"user_prompt": prompt, "urls": source}
        actual_inputs = mock_execute.call_args[0][0]
        assert actual_inputs == expected_inputs

    @pytest.mark.asyncio
    @patch('scrapegraphai.graphs.script_creator_multi_graph.GraphIteratorNode')
    @patch('scrapegraphai.graphs.script_creator_multi_graph.MergeGeneratedScriptsNode')
    @patch('scrapegraphai.graphs.script_creator_multi_graph.BaseGraph.execute')
    async def test_run_with_empty_scripts_list(self, mock_execute, mock_merge_node, mock_iterator_node):
        """
        Test the ScriptCreatorMultiGraph.run() method when the GraphIteratorNode returns an empty list of scripts.
        This test checks if the graph handles the case when no scripts are generated from the input URLs.
        """
        # Arrange
        prompt = "What is Chioggia famous for?"
        source = ["https://example.com/chioggia"]
        config = {"llm": {"model": "openai/gpt-3.5-turbo"}}

        # Mock the GraphIteratorNode to return an empty list of scripts
        mock_iterator_node.return_value.execute.return_value = ({"scripts": []}, {})

        # Mock the MergeGeneratedScriptsNode to return a failure message
        mock_merge_node.return_value.execute.return_value = ({"merged_script": "No scripts were generated."}, {})

        # Mock the BaseGraph.execute to return the result of MergeGeneratedScriptsNode
        mock_execute.return_value = ({"merged_script": "No scripts were generated."}, {})

        graph = ScriptCreatorMultiGraph(prompt, source, config)

        # Act
        result = graph.run()

        # Assert
        assert result == "No scripts were generated."
        mock_iterator_node.assert_called_once()
        mock_merge_node.assert_called_once()
        mock_execute.assert_called_once()

        # Check if MergeGeneratedScriptsNode was called with an empty list of scripts
        merge_node_inputs = mock_merge_node.return_value.execute.call_args[0][0]
        assert merge_node_inputs['scripts'] == []

    @pytest.mark.asyncio
    @patch('scrapegraphai.graphs.script_creator_multi_graph.BaseGraph')
    @patch('scrapegraphai.graphs.script_creator_multi_graph.GraphIteratorNode')
    @patch('scrapegraphai.graphs.script_creator_multi_graph.MergeGeneratedScriptsNode')
    async def test_custom_embedder_model_configuration(self, mock_merge_node, mock_iterator_node, mock_base_graph):
        """
        Test that a custom embedder model configuration is correctly passed to the graph nodes
        when initializing ScriptCreatorMultiGraph.
        """
        # Arrange
        prompt = "What is Chioggia famous for?"
        source = ["https://example.com/chioggia"]
        config = {
            "llm": {"model": "openai/gpt-3.5-turbo"},
            "embedder": {"model": "custom/embedder-model"}
        }

        # Act
        graph = ScriptCreatorMultiGraph(prompt, source, config)

        # Assert
        mock_iterator_node.assert_called_once()
        iterator_node_config = mock_iterator_node.call_args[1]['node_config']
        assert 'scraper_config' in iterator_node_config
        assert iterator_node_config['scraper_config']['embedder']['model'] == "custom/embedder-model"

        mock_merge_node.assert_called_once()
        merge_node_config = mock_merge_node.call_args[1]['node_config']
        assert 'llm_model' in merge_node_config
        assert merge_node_config['llm_model']['model'] == "openai/gpt-3.5-turbo"

        mock_base_graph.assert_called_once()

    @pytest.mark.asyncio
    async def test_custom_model_token_limit(self):
        """
        Test that a custom model token limit is correctly set when initializing ScriptCreatorMultiGraph.
        This test verifies that the model_token attribute is set correctly and that it's included in the copy_config.
        """
        # Arrange
        prompt = "What is Chioggia famous for?"
        source = ["https://example.com/chioggia"]
        custom_token_limit = 2000
        config = {
            "llm": {"model": "openai/gpt-3.5-turbo"},
            "model_token": custom_token_limit
        }

        # Act
        graph = ScriptCreatorMultiGraph(prompt, source, config)

        # Assert
        assert graph.model_token == custom_token_limit
        assert graph.copy_config['model_token'] == custom_token_limit
        assert graph.copy_config is not config
        assert graph.copy_config == config  # We use == instead of deepcopy for simplicity