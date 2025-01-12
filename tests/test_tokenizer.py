import pytest

from scrapegraphai.utils.tokenizer import num_tokens_calculus
from unittest.mock import patch

class TestTokenizer:
    @patch('scrapegraphai.utils.tokenizer.num_tokens_openai')
    def test_num_tokens_calculus_calls_openai_tokenizer(self, mock_num_tokens_openai):
        # Arrange
        test_string = "This is a test string"
        expected_tokens = 5
        mock_num_tokens_openai.return_value = expected_tokens

        # Act
        result = num_tokens_calculus(test_string)

        # Assert
        mock_num_tokens_openai.assert_called_once_with(test_string)
        assert result == expected_tokens