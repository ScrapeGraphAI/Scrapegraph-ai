"""
Test fo testing the tokenizer
"""
import unittest
from scrapegraphai.utils.token_calculator import truncate_text_tokens


class TestTruncateTextTokens(unittest.TestCase):
    """ 
    Class for testing the tokenizer
    """

    def test_truncate_text_tokens(self):
        """ 
        Principal text
        """
        input_text = "This is a sample text to be tokenized into chunks."
        expected_output = [
            "This is a sample text to be tokenized into",
            "chunks."
        ]
        model_name = "gpt-3.5-turbo"
        encoding_name = "EMBEDDING_ENCODING"

        output_chunks = truncate_text_tokens(
            input_text, model_name, encoding_name)

        self.assertEqual(output_chunks, expected_output)


if __name__ == '__main__':
    unittest.main()
