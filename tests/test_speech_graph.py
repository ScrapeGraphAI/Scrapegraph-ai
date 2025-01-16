import unittest

from pydantic import BaseModel
from scrapegraphai.graphs.speech_graph import SpeechGraph
from scrapegraphai.models.openai_tts import OpenAITextToSpeech
from unittest.mock import MagicMock, patch

class TestSpeechGraph(unittest.TestCase):
    @patch('scrapegraphai.graphs.speech_graph.BaseGraph')
    @patch('scrapegraphai.graphs.abstract_graph.init_chat_model')
    @patch('scrapegraphai.models.openai_tts.OpenAI')
    def test_speech_graph_initialization(self, mock_openai, mock_init_chat_model, mock_base_graph):
        """
        Test the initialization of SpeechGraph with both URL and local directory sources.
        This test covers the scenario where input_key is set correctly based on the source,
        and ensures that the graph is created with the proper configuration.
        """
        # Arrange
        prompt = "Summarize the contents"
        config = {
            "llm": {"model": "openai/gpt-3.5-turbo"},
            "tts_model": {
                "api_key": "test_api_key",
                "base_url": "https://api.openai.com/v1"
            }
        }

        class TestSchema(BaseModel):
            summary: str

        # Mock the LLM initialization
        mock_llm = MagicMock()
        mock_init_chat_model.return_value = mock_llm

        # Test with URL source
        url_source = "https://example.com"
        url_speech_graph = SpeechGraph(prompt, url_source, config, TestSchema)

        # Assert for URL source
        self.assertEqual(url_speech_graph.input_key, "url")
        self.assertEqual(url_speech_graph.prompt, prompt)
        self.assertEqual(url_speech_graph.source, url_source)
        self.assertEqual(url_speech_graph.config, config)
        self.assertEqual(url_speech_graph.schema, TestSchema)

        # Test with local directory source
        local_source = "/path/to/local/directory"
        local_speech_graph = SpeechGraph(prompt, local_source, config, TestSchema)

        # Assert for local directory source
        self.assertEqual(local_speech_graph.input_key, "local_dir")
        self.assertEqual(local_speech_graph.prompt, prompt)
        self.assertEqual(local_speech_graph.source, local_source)
        self.assertEqual(local_speech_graph.config, config)
        self.assertEqual(local_speech_graph.schema, TestSchema)

        # Verify that _create_graph was called for both instances
        self.assertEqual(mock_base_graph.call_count, 2)

        # Verify that OpenAI client was initialized with the correct configuration
        mock_openai.assert_called_with(api_key="test_api_key", base_url="https://api.openai.com/v1")

        # Verify that the graph attribute is set for both instances
        self.assertIsNotNone(url_speech_graph.graph)
        self.assertIsNotNone(local_speech_graph.graph)

    @patch('scrapegraphai.graphs.speech_graph.BaseGraph')
    @patch('scrapegraphai.graphs.abstract_graph.init_chat_model')
    @patch('scrapegraphai.models.openai_tts.OpenAI')
    def test_speech_graph_initialization(self, mock_openai, mock_init_chat_model, mock_base_graph):
        """
        Test the initialization of SpeechGraph with both URL and local directory sources.
        This test covers the scenario where input_key is set correctly based on the source,
        ensures that the graph is created with the proper configuration, and verifies
        that the OpenAI client for text-to-speech is initialized correctly.
        """
        # Arrange
        prompt = "Summarize the contents"
        config = {
            "llm": {"model": "openai/gpt-3.5-turbo"},
            "tts_model": {
                "api_key": "test_api_key",
                "base_url": "https://api.openai.com/v1"
            }
        }

        class TestSchema(BaseModel):
            summary: str

        # Mock the LLM initialization
        mock_llm = MagicMock()
        mock_init_chat_model.return_value = mock_llm

        # Test with URL source
        url_source = "https://example.com"
        url_speech_graph = SpeechGraph(prompt, url_source, config, TestSchema)

        # Assert for URL source
        self.assertEqual(url_speech_graph.input_key, "url")
        self.assertEqual(url_speech_graph.prompt, prompt)
        self.assertEqual(url_speech_graph.source, url_source)
        self.assertEqual(url_speech_graph.config, config)
        self.assertEqual(url_speech_graph.schema, TestSchema)

        # Test with local directory source
        local_source = "/path/to/local/directory"
        local_speech_graph = SpeechGraph(prompt, local_source, config, TestSchema)

        # Assert for local directory source
        self.assertEqual(local_speech_graph.input_key, "local_dir")
        self.assertEqual(local_speech_graph.prompt, prompt)
        self.assertEqual(local_speech_graph.source, local_source)
        self.assertEqual(local_speech_graph.config, config)
        self.assertEqual(local_speech_graph.schema, TestSchema)

        # Verify that _create_graph was called for both instances
        self.assertEqual(mock_base_graph.call_count, 2)

        # Verify that OpenAI client was initialized with the correct configuration
        mock_openai.assert_called_with(api_key="test_api_key", base_url="https://api.openai.com/v1")

        # Verify that the graph attribute is set for both instances
        self.assertIsNotNone(url_speech_graph.graph)
        self.assertIsNotNone(local_speech_graph.graph)

    @patch('scrapegraphai.graphs.speech_graph.BaseGraph')
    @patch('scrapegraphai.graphs.abstract_graph.init_chat_model')
    @patch('scrapegraphai.models.openai_tts.OpenAI')
    def test_speech_graph_initialization(self, mock_openai, mock_init_chat_model, mock_base_graph):
        """
        Test the initialization of SpeechGraph with both URL and local directory sources.
        This test covers the scenario where input_key is set correctly based on the source,
        ensures that the graph is created with the proper configuration, and verifies
        that the OpenAI client for text-to-speech is initialized correctly.
        """
        # Arrange
        prompt = "Summarize the contents"
        config = {
            "llm": {"model": "openai/gpt-3.5-turbo"},
            "tts_model": {
                "api_key": "test_api_key",
                "base_url": "https://api.openai.com/v1"
            },
            "output_path": "test_output.mp3"
        }

        class TestSchema(BaseModel):
            summary: str

        # Mock the LLM initialization
        mock_llm = MagicMock()
        mock_init_chat_model.return_value = mock_llm

        # Test with URL source
        url_source = "https://example.com"
        url_speech_graph = SpeechGraph(prompt, url_source, config, TestSchema)

        # Assert for URL source
        self.assertEqual(url_speech_graph.input_key, "url")
        self.assertEqual(url_speech_graph.prompt, prompt)
        self.assertEqual(url_speech_graph.source, url_source)
        self.assertEqual(url_speech_graph.config, config)
        self.assertEqual(url_speech_graph.schema, TestSchema)

        # Test with local directory source
        local_source = "/path/to/local/directory"
        local_speech_graph = SpeechGraph(prompt, local_source, config, TestSchema)

        # Assert for local directory source
        self.assertEqual(local_speech_graph.input_key, "local_dir")
        self.assertEqual(local_speech_graph.prompt, prompt)
        self.assertEqual(local_speech_graph.source, local_source)
        self.assertEqual(local_speech_graph.config, config)
        self.assertEqual(local_speech_graph.schema, TestSchema)

        # Verify that _create_graph was called for both instances
        self.assertEqual(mock_base_graph.call_count, 2)

        # Verify that OpenAI client was initialized with the correct configuration
        mock_openai.assert_called_with(api_key="test_api_key", base_url="https://api.openai.com/v1")

        # Verify that the graph attribute is set for both instances
        self.assertIsNotNone(url_speech_graph.graph)
        self.assertIsNotNone(local_speech_graph.graph)

    @patch('scrapegraphai.graphs.speech_graph.BaseGraph')
    @patch('scrapegraphai.graphs.abstract_graph.init_chat_model')
    @patch('scrapegraphai.graphs.speech_graph.save_audio_from_bytes')
    def test_speech_graph_run(self, mock_save_audio, mock_init_chat_model, mock_base_graph):
        """
        Test the run method of SpeechGraph to ensure it executes the graph and saves the audio output.
        """
        # Arrange
        prompt = "Summarize the contents"
        source = "https://example.com"
        config = {
            "llm": {"model": "openai/gpt-3.5-turbo"},
            "tts_model": {
                "api_key": "test_api_key",
                "base_url": "https://api.openai.com/v1"
            },
            "output_path": "test_output.mp3"
        }

        mock_llm = MagicMock()
        mock_init_chat_model.return_value = mock_llm

        mock_graph = MagicMock()
        mock_graph.execute.return_value = ({"answer": "Test answer", "audio": b"fake_audio_data"}, {})
        mock_base_graph.return_value = mock_graph

        speech_graph = SpeechGraph(prompt, source, config)

        # Act
        result = speech_graph.run()

        # Assert
        self.assertEqual(result, "Test answer")
        mock_graph.execute.assert_called_once_with({"user_prompt": prompt, "url": source})
        mock_save_audio.assert_called_once_with(b"fake_audio_data", "test_output.mp3")