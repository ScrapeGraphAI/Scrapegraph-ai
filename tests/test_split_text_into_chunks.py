import pytest

from scrapegraphai.utils.split_text_into_chunks import split_text_into_chunks
from unittest.mock import Mock, patch

class TestSplitTextIntoChunks:
    def test_split_text_without_semchunk(self):
        # Test splitting text without using semchunk
        text = "This is a test sentence. It should be split into chunks based on token count."
        chunk_size = 10
        expected_chunks = [
            "This is a test sentence.",
            "It should be split into chunks",
            "based on token count."
        ]

        result = split_text_into_chunks(text, chunk_size, use_semchunk=False)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"

    @patch('scrapegraphai.utils.split_text_into_chunks.chunk')
    def test_split_text_with_semchunk(self, mock_chunk):
        # Test splitting text using semchunk
        text = "This is a test sentence. It should be split into chunks based on token count."
        chunk_size = 10
        expected_chunks = [
            "This is a test sentence.",
            "It should be split into chunks",
            "based on token count."
        ]

        # Mock the semchunk.chunk function to return our expected chunks
        mock_chunk.return_value = expected_chunks

        result = split_text_into_chunks(text, chunk_size, use_semchunk=True)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"
        mock_chunk.assert_called_once()

    def test_short_text_no_splitting(self):
        # Test when the input text is shorter than the chunk size
        text = "This is a short text."
        chunk_size = 50  # Larger than the token count of the input text
        expected_chunks = [text]  # The entire text should be returned as a single chunk

        result = split_text_into_chunks(text, chunk_size, use_semchunk=False)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"
        assert len(result) == 1, f"Expected 1 chunk, but got {len(result)}"

    def test_very_small_chunk_size(self):
        # Test splitting text with a very small chunk size
        text = "This is a test with small chunks."
        chunk_size = 3  # Very small chunk size
        expected_chunks = [
            "This",
            "is",
            "a",
            "test",
            "with",
            "small",
            "chunks."
        ]

        result = split_text_into_chunks(text, chunk_size, use_semchunk=False)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"
        assert len(result) == len(expected_chunks), f"Expected {len(expected_chunks)} chunks, but got {len(result)}"

    @patch('scrapegraphai.utils.split_text_into_chunks.num_tokens_calculus')
    def test_chunk_size_equal_to_token_count(self, mock_num_tokens):
        # Test when chunk size is exactly equal to the token count of the input text
        text = "This is a test sentence with exact token count."
        chunk_size = 10  # Set to match the mocked token count
        expected_chunks = [text]  # The entire text should be returned as a single chunk

        # Mock num_tokens_calculus to always return the chunk_size
        mock_num_tokens.return_value = chunk_size

        result = split_text_into_chunks(text, chunk_size, use_semchunk=False)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"
        assert len(result) == 1, f"Expected 1 chunk, but got {len(result)}"
        mock_num_tokens.assert_called_with(text)

    @patch('scrapegraphai.utils.split_text_into_chunks.chunk')
    @patch('scrapegraphai.utils.split_text_into_chunks.num_tokens_calculus')
    def test_large_chunk_size_with_semchunk(self, mock_num_tokens, mock_chunk):
        # Test splitting text using semchunk with a large chunk size
        text = "This is a test sentence for large chunk size."
        large_chunk_size = 1000
        expected_adjusted_chunk_size = int(large_chunk_size * 0.9)
        expected_chunks = ["This is a test sentence", "for large chunk size."]

        # Mock num_tokens_calculus to return a consistent value
        mock_num_tokens.return_value = 5

        # Mock the semchunk.chunk function to return our expected chunks
        mock_chunk.return_value = expected_chunks

        result = split_text_into_chunks(text, large_chunk_size, use_semchunk=True)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"
        mock_chunk.assert_called_once_with(
            text=text,
            chunk_size=expected_adjusted_chunk_size,
            token_counter=mock_num_tokens.return_value,
            memoize=False
        )
        assert mock_num_tokens.call_count > 0, "num_tokens_calculus should have been called"

    @patch('scrapegraphai.utils.split_text_into_chunks.num_tokens_calculus')
    def test_split_text_with_long_words(self, mock_num_tokens):
        # Test splitting text with very long words
        text = "Short verylongwordthatexceedschunksize another extremelylongwordthatalsosexceedschunksize end."
        chunk_size = 10

        # Mock num_tokens_calculus to return the length of each word
        mock_num_tokens.side_effect = lambda word: len(word)

        expected_chunks = [
            "Short",
            "verylongwordthatexceedschunksize",
            "another",
            "extremelylongwordthatalsosexceedschunksize",
            "end."
        ]

        result = split_text_into_chunks(text, chunk_size, use_semchunk=False)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"
        assert len(result) == len(expected_chunks), f"Expected {len(expected_chunks)} chunks, but got {len(result)}"

        # Verify that num_tokens_calculus was called for each word
        assert mock_num_tokens.call_count == len(text.split())

    @patch('scrapegraphai.utils.split_text_into_chunks.num_tokens_calculus')
    def test_split_text_with_newlines(self, mock_num_tokens):
        # Test splitting text that contains newline characters
        text = "This is a test\nwith multiple lines.\nIt should split correctly."
        chunk_size = 15

        # Mock num_tokens_calculus to return a fixed value for simplicity
        mock_num_tokens.return_value = 1

        expected_chunks = [
            "This is a test",
            "with multiple",
            "lines. It should",
            "split correctly."
        ]

        result = split_text_into_chunks(text, chunk_size, use_semchunk=False)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"
        assert len(result) == len(expected_chunks), f"Expected {len(expected_chunks)} chunks, but got {len(result)}"

        # Verify that num_tokens_calculus was called for each word
        assert mock_num_tokens.call_count == len(text.split())

        # Check that newlines are preserved within chunks
        assert "\n" in result[1], "Newline should be preserved in the second chunk"

    @patch('scrapegraphai.utils.split_text_into_chunks.num_tokens_calculus')
    def test_split_text_with_unicode_characters(self, mock_num_tokens):
        # Test splitting text that contains Unicode characters
        text = "This is a test with Unicode: 你好世界! Здравствуй, мир! 🌍🌎🌏"
        chunk_size = 10

        # Mock num_tokens_calculus to return a fixed value for simplicity
        mock_num_tokens.return_value = 1

        expected_chunks = [
            "This is a test",
            "with Unicode:",
            "你好世界!",
            "Здравствуй,",
            "мир! 🌍🌎🌏"
        ]

        result = split_text_into_chunks(text, chunk_size, use_semchunk=False)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"
        assert len(result) == len(expected_chunks), f"Expected {len(expected_chunks)} chunks, but got {len(result)}"

        # Verify that num_tokens_calculus was called for each word or character
        assert mock_num_tokens.call_count == len(text.split())

        # Check that Unicode characters are preserved in chunks
        assert "你好世界!" in result, "Chinese characters should be preserved in a chunk"
        assert "Здравствуй," in result, "Cyrillic characters should be preserved in a chunk"
        assert "🌍🌎🌏" in result[-1], "Emojis should be preserved in the last chunk"

    @patch('scrapegraphai.utils.split_text_into_chunks.num_tokens_calculus')
    def test_split_text_with_multiple_spaces(self, mock_num_tokens):
        # Test splitting text that contains multiple spaces between words
        text = "This   is  a   test   with   multiple   spaces."
        chunk_size = 10

        # Mock num_tokens_calculus to return 1 for each word, ignoring spaces
        mock_num_tokens.side_effect = lambda word: 1 if word.strip() else 0

        expected_chunks = [
            "This   is  a",
            "test   with",
            "multiple",
            "spaces."
        ]

        result = split_text_into_chunks(text, chunk_size, use_semchunk=False)

        assert result == expected_chunks, f"Expected {expected_chunks}, but got {result}"
        assert len(result) == len(expected_chunks), f"Expected {len(expected_chunks)} chunks, but got {len(result)}"

        # Verify that num_tokens_calculus was called for each word and space
        assert mock_num_tokens.call_count == len(text.split()) + text.count('   ')

        # Check that multiple spaces are preserved within chunks
        assert "   " in result[0], "Multiple spaces should be preserved in the first chunk"
        assert "   " in result[1], "Multiple spaces should be preserved in the second chunk"