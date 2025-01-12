import unittest

from scrapegraphai.utils.tokenizers.tokenizer_openai import num_tokens_openai
from unittest.mock import MagicMock, patch

class TestTokenizerOpenAI(unittest.TestCase):
    @patch('scrapegraphai.utils.tokenizers.tokenizer_openai.get_logger')
    @patch('scrapegraphai.utils.tokenizers.tokenizer_openai.tiktoken')
    def test_num_tokens_openai_simple_input(self, mock_tiktoken, mock_get_logger):
        # Arrange
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        mock_encoding = MagicMock()
        mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # Simulating 5 tokens
        mock_tiktoken.encoding_for_model.return_value = mock_encoding

        test_text = "This is a test sentence."

        # Act
        result = num_tokens_openai(test_text)

        # Assert
        self.assertEqual(result, 5)
        mock_logger.debug.assert_called_once_with(f"Counting tokens for text of {len(test_text)} characters")
        mock_tiktoken.encoding_for_model.assert_called_once_with("gpt-4o")
        mock_encoding.encode.assert_called_once_with(test_text)

if __name__ == '__main__':
    unittest.main()