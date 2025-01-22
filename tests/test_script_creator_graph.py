import unittest

from pydantic import BaseModel
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