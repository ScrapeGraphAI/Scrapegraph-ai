import unittest

from pydantic import BaseModel
from scrapegraphai.graphs.base_graph import BaseGraph
from scrapegraphai.graphs.script_creator_graph import ScriptCreatorGraph
from unittest.mock import MagicMock, patch

class TestScriptCreatorGraph(unittest.TestCase):
    def test_init_with_local_dir(self):
        """
        Test initializing ScriptCreatorGraph with a local directory source.
        This test verifies that the input_key is set correctly for local sources.
        """
        prompt = "Generate a script to scrape local HTML files"
        source = "/path/to/local/directory"
        config = {
            "library": "beautifulsoup",
            "llm": {"model": "mock_model"}
        }

        with patch('scrapegraphai.graphs.script_creator_graph.AbstractGraph.__init__') as mock_init:
            graph = ScriptCreatorGraph(prompt, source, config)

            mock_init.assert_called_once_with(prompt, config, source, None)
            self.assertEqual(graph.library, "beautifulsoup")
            self.assertEqual(graph.input_key, "local_dir")

    @patch('scrapegraphai.graphs.abstract_graph.AbstractGraph.__init__')
    @patch('scrapegraphai.graphs.base_graph.BaseGraph')
    def test_run_method(self, mock_base_graph, mock_abstract_init):
        """
        Test the run method of ScriptCreatorGraph.
        This test verifies that the run method correctly executes the graph
        and returns the expected answer for both successful and unsuccessful scenarios.
        """
        # Setup
        prompt = "Test prompt"
        source = "https://example.com"
        config = {
            "library": "beautifulsoup",
            "llm": {"model": "mock_model"}
        }

        # Mock AbstractGraph.__init__
        mock_abstract_init.return_value = None

        # Create ScriptCreatorGraph instance
        graph = ScriptCreatorGraph(prompt, source, config)

        # Set necessary attributes manually
        graph.prompt = prompt
        graph.source = source
        graph.input_key = "url"
        graph.model_token = 1000

        # Mock BaseGraph instance
        mock_graph_instance = MagicMock()
        mock_base_graph.return_value = mock_graph_instance
        graph.graph = mock_graph_instance

        # Test successful scenario
        mock_graph_instance.execute.return_value = ({"answer": "Mocked answer"}, None)
        result = graph.run()
        self.assertEqual(result, "Mocked answer")
        mock_graph_instance.execute.assert_called_once_with({
            "user_prompt": prompt,
            "url": source
        })

        # Test unsuccessful scenario (no answer found)
        mock_graph_instance.execute.return_value = ({}, None)
        result = graph.run()
        self.assertEqual(result, "No answer found ")

        # Verify that execute was called twice in total
        self.assertEqual(mock_graph_instance.execute.call_count, 2)

    @patch('scrapegraphai.graphs.abstract_graph.AbstractGraph.__init__')
    def test_run_method(self, mock_abstract_init):
        """
        Test the run method of ScriptCreatorGraph.
        This test verifies that:
        1. The run method correctly executes the graph and returns the expected answer.
        2. The input to the graph execution is correctly constructed.
        3. The method handles both successful and unsuccessful scenarios.
        """
        # Setup
        prompt = "Test prompt"
        source = "https://example.com"
        config = {
            "library": "beautifulsoup",
            "llm": {"model": "mock_model"}
        }

        # Mock AbstractGraph.__init__
        mock_abstract_init.return_value = None

        # Create ScriptCreatorGraph instance
        graph = ScriptCreatorGraph(prompt, source, config)

        # Set necessary attributes manually
        graph.prompt = prompt
        graph.source = source
        graph.input_key = "url"
        graph.model_token = 1000

        # Mock graph execution
        mock_base_graph = MagicMock()
        graph.graph = mock_base_graph

        # Test successful scenario
        mock_base_graph.execute.return_value = ({"answer": "Mocked answer"}, None)
        result = graph.run()

        # Assertions for successful scenario
        self.assertEqual(result, "Mocked answer")
        mock_base_graph.execute.assert_called_once_with({
            "user_prompt": prompt,
            "url": source
        })

        # Reset mock for next test
        mock_base_graph.execute.reset_mock()

        # Test unsuccessful scenario (no answer found)
        mock_base_graph.execute.return_value = ({}, None)
        result = graph.run()

        # Assertions for unsuccessful scenario
        self.assertEqual(result, "No answer found ")
        mock_base_graph.execute.assert_called_once_with({
            "user_prompt": prompt,
            "url": source
        })

    @patch('scrapegraphai.graphs.abstract_graph.AbstractGraph.__init__')
    @patch('scrapegraphai.graphs.script_creator_graph.ScriptCreatorGraph._create_graph')
    def test_run_method(self, mock_create_graph, mock_abstract_init):
        """
        Test the run method of ScriptCreatorGraph.
        This test verifies that:
        1. The ScriptCreatorGraph is initialized correctly.
        2. The run method executes the graph and returns the expected answer.
        3. The input to the graph execution is correctly constructed.
        4. The method handles both successful and unsuccessful scenarios.
        """
        # Setup
        prompt = "Test prompt"
        source = "https://example.com"
        config = {
            "library": "beautifulsoup",
            "llm": {"model": "mock_model"}
        }

        # Mock AbstractGraph.__init__
        mock_abstract_init.return_value = None

        # Create ScriptCreatorGraph instance
        graph = ScriptCreatorGraph(prompt, source, config)

        # Set necessary attributes manually
        graph.prompt = prompt
        graph.source = source
        graph.input_key = "url"
        graph.model_token = 1000

        # Mock graph creation and execution
        mock_base_graph = MagicMock()
        mock_create_graph.return_value = mock_base_graph
        graph.graph = mock_base_graph

        # Test successful scenario
        mock_base_graph.execute.return_value = ({"answer": "Mocked answer"}, None)
        result = graph.run()

        # Assertions for successful scenario
        self.assertEqual(result, "Mocked answer")
        mock_base_graph.execute.assert_called_once_with({
            "user_prompt": prompt,
            "url": source
        })

        # Reset mock for next test
        mock_base_graph.execute.reset_mock()

        # Test unsuccessful scenario (no answer found)
        mock_base_graph.execute.return_value = ({}, None)
        result = graph.run()

        # Assertions for unsuccessful scenario
        self.assertEqual(result, "No answer found ")
        mock_base_graph.execute.assert_called_once_with({
            "user_prompt": prompt,
            "url": source
        })

    @patch('scrapegraphai.graphs.abstract_graph.AbstractGraph.__init__')
    @patch('scrapegraphai.graphs.script_creator_graph.ScriptCreatorGraph._create_graph')
    def test_run_method(self, mock_create_graph, mock_abstract_init):
        """
        Test the run method of ScriptCreatorGraph.
        This test verifies that:
        1. The ScriptCreatorGraph is initialized correctly.
        2. The run method executes the graph and returns the expected answer.
        3. The input to the graph execution is correctly constructed.
        4. The method handles both successful and unsuccessful scenarios.
        """
        # Setup
        prompt = "Test prompt"
        source = "https://example.com"
        config = {
            "library": "beautifulsoup",
            "llm": {"model": "mock_model"}
        }

        # Mock AbstractGraph.__init__
        mock_abstract_init.return_value = None

        # Create ScriptCreatorGraph instance
        graph = ScriptCreatorGraph(prompt, source, config)

        # Set necessary attributes manually
        graph.prompt = prompt
        graph.source = source
        graph.input_key = "url"
        graph.model_token = 1000

        # Mock graph creation and execution
        mock_base_graph = MagicMock()
        mock_create_graph.return_value = mock_base_graph
        graph.graph = mock_base_graph

        # Test successful scenario
        mock_base_graph.execute.return_value = ({"answer": "Mocked answer"}, None)
        result = graph.run()

        # Assertions for successful scenario
        self.assertEqual(result, "Mocked answer")
        mock_base_graph.execute.assert_called_once_with({
            "user_prompt": prompt,
            "url": source
        })

        # Reset mock for next test
        mock_base_graph.execute.reset_mock()

        # Test unsuccessful scenario (no answer found)
        mock_base_graph.execute.return_value = ({}, None)
        result = graph.run()

        # Assertions for unsuccessful scenario
        self.assertEqual(result, "No answer found ")
        mock_base_graph.execute.assert_called_once_with({
            "user_prompt": prompt,
            "url": source
        })

    @patch('scrapegraphai.graphs.abstract_graph.AbstractGraph.__init__')
    @patch('scrapegraphai.graphs.script_creator_graph.ScriptCreatorGraph._create_graph')
    def test_run_method(self, mock_create_graph, mock_abstract_init):
        """
        Test the run method of ScriptCreatorGraph.
        This test verifies that:
        1. The ScriptCreatorGraph is initialized correctly.
        2. The run method executes the graph and returns the expected answer.
        3. The input to the graph execution is correctly constructed.
        4. The method handles both successful and unsuccessful scenarios.
        """
        # Setup
        prompt = "Test prompt"
        source = "https://example.com"
        config = {
            "library": "beautifulsoup",
            "llm": {"model": "mock_model"}
        }

        # Mock AbstractGraph.__init__
        mock_abstract_init.return_value = None

        # Create ScriptCreatorGraph instance
        graph = ScriptCreatorGraph(prompt, source, config)

        # Set necessary attributes manually
        graph.prompt = prompt
        graph.source = source
        graph.input_key = "url"
        graph.model_token = 1000

        # Mock graph creation and execution
        mock_base_graph = MagicMock()
        mock_create_graph.return_value = mock_base_graph
        graph.graph = mock_base_graph

        # Test successful scenario
        mock_base_graph.execute.return_value = ({"answer": "Mocked answer"}, None)
        result = graph.run()

        # Assertions for successful scenario
        self.assertEqual(result, "Mocked answer")
        mock_base_graph.execute.assert_called_once_with({
            "user_prompt": prompt,
            "url": source
        })

        # Reset mock for next test
        mock_base_graph.execute.reset_mock()

        # Test unsuccessful scenario (no answer found)
        mock_base_graph.execute.return_value = ({}, None)
        result = graph.run()

        # Assertions for unsuccessful scenario
        self.assertEqual(result, "No answer found ")
        mock_base_graph.execute.assert_called_once_with({
            "user_prompt": prompt,
            "url": source
        })