import pytest

from langchain_community.document_transformers import Html2TextTransformer
from langchain_core.documents import Document
from scrapegraphai.nodes.parse_node import ParseNode
from unittest.mock import MagicMock, patch

class TestParseNode:

    def test_extract_relative_urls(self):
        # Setup
        node_config = {
            "verbose": True,
            "parse_html": False,
            "parse_urls": True,
            "chunk_size": 1000
        }
        parse_node = ParseNode(
            input="input,source",
            output=["chunks", "link_urls", "img_urls"],
            node_config=node_config
        )

        # Mock input data
        mock_document = Document(page_content="Check out this <a href='/relative/path'>relative link</a> and this <img src='/images/photo.jpg'>")
        mock_source = "https://example.com"

        mock_state = {
            "input": [mock_document],
            "source": mock_source
        }

        # Execute
        result_state = parse_node.execute(mock_state)

        # Assert
        assert "chunks" in result_state
        assert "link_urls" in result_state
        assert "img_urls" in result_state

        assert "https://example.com/relative/path" in result_state["link_urls"]
        assert "https://example.com/images/photo.jpg" in result_state["img_urls"]

    def test_parse_html_content(self):
        # Setup
        node_config = {
            "verbose": True,
            "parse_html": True,
            "parse_urls": False,
            "chunk_size": 1000
        }
        parse_node = ParseNode(
            input="input",
            output=["chunks"],
            node_config=node_config
        )

        # Mock input data
        html_content = "<html><body><h1>Test Header</h1><p>This is a test paragraph.</p></body></html>"
        mock_document = Document(page_content=html_content)
        mock_state = {
            "input": [mock_document]
        }

        # Mock Html2TextTransformer
        mock_transformed_doc = Document(page_content="Test Header\n\nThis is a test paragraph.")
        mock_transformer = MagicMock()
        mock_transformer.transform_documents.return_value = [mock_transformed_doc]

        # Execute with mocked Html2TextTransformer
        with patch('scrapegraphai.nodes.parse_node.Html2TextTransformer', return_value=mock_transformer):
            result_state = parse_node.execute(mock_state)

        # Assert
        assert "chunks" in result_state
        assert len(result_state["chunks"]) > 0
        assert "Test Header" in result_state["chunks"][0]
        assert "This is a test paragraph" in result_state["chunks"][0]

    def test_parse_urls_without_html_parsing(self):
        # Setup
        node_config = {
            "verbose": True,
            "parse_html": False,
            "parse_urls": True,
            "chunk_size": 1000
        }
        parse_node = ParseNode(
            input="input,source",
            output=["chunks", "link_urls", "img_urls"],
            node_config=node_config
        )

        # Mock input data
        text_content = "Check out https://example.com and /relative/path.html. Also, see image.jpg"
        mock_document = Document(page_content=text_content)
        mock_source = "https://sourcesite.com"

        mock_state = {
            "input": [mock_document],
            "source": mock_source
        }

        # Execute
        result_state = parse_node.execute(mock_state)

        # Assert
        assert "chunks" in result_state
        assert "link_urls" in result_state
        assert "img_urls" in result_state

        assert "https://example.com" in result_state["link_urls"]
        assert "https://sourcesite.com/relative/path.html" in result_state["link_urls"]
        assert "https://sourcesite.com/image.jpg" in result_state["img_urls"]
        assert len(result_state["chunks"]) > 0
        assert text_content in result_state["chunks"][0]

    def test_large_document_chunking(self):
        # Setup
        node_config = {
            "verbose": False,
            "parse_html": False,
            "parse_urls": False,
            "chunk_size": 100  # Small chunk size for testing
        }
        parse_node = ParseNode(
            input="input",
            output=["chunks"],
            node_config=node_config
        )

        # Create a large document
        large_content = "This is a test sentence. " * 50  # 1250 characters
        mock_document = Document(page_content=large_content)
        mock_state = {
            "input": [mock_document]
        }

        # Execute
        result_state = parse_node.execute(mock_state)

        # Assert
        assert "chunks" in result_state
        chunks = result_state["chunks"]

        # Check if we have the expected number of chunks
        expected_chunks = 13  # 1250 / 100 = 12.5, rounded up to 13
        assert len(chunks) == expected_chunks, f"Expected {expected_chunks} chunks, but got {len(chunks)}"

        # Check if each chunk is approximately the right size
        for chunk in chunks[:-1]:  # All but the last chunk
            assert 80 <= len(chunk) <= 100, f"Chunk size {len(chunk)} is out of expected range"

        # Check if the content is preserved
        reconstructed_content = " ".join(chunks)
        assert reconstructed_content.strip() == large_content.strip(), "Content was not preserved after chunking"

    def test_missing_input_keys(self):
        # Setup
        node_config = {
            "verbose": False,
            "parse_html": True,
            "parse_urls": True,
            "chunk_size": 1000
        }
        parse_node = ParseNode(
            input="input,source",
            output=["chunks", "link_urls", "img_urls"],
            node_config=node_config
        )

        # Create a state with missing input keys
        incomplete_state = {}

        # Execute and assert
        with pytest.raises(KeyError) as excinfo:
            parse_node.execute(incomplete_state)

        # Check if the error message contains information about missing keys
        assert "input" in str(excinfo.value) or "source" in str(excinfo.value), \
            "KeyError should mention missing input keys"

    def test_invalid_url_handling(self):
        # Setup
        node_config = {
            "verbose": False,
            "parse_html": False,
            "parse_urls": True,
            "chunk_size": 1000
        }
        parse_node = ParseNode(
            input="input,source",
            output=["chunks", "link_urls", "img_urls"],
            node_config=node_config
        )

        # Mock input data with an invalid URL
        invalid_url = "http://invalid[url].com"
        text_content = f"Check out this invalid URL: {invalid_url}"
        mock_document = Document(page_content=text_content)
        mock_source = "https://example.com"

        mock_state = {
            "input": [mock_document],
            "source": mock_source
        }

        # Execute
        result_state = parse_node.execute(mock_state)

        # Assert
        assert "chunks" in result_state
        assert "link_urls" in result_state
        assert "img_urls" in result_state

        # Check that the invalid URL is not in the extracted URLs
        assert invalid_url not in result_state["link_urls"]

        # Check that the chunk still contains the original text
        assert text_content in result_state["chunks"][0]

        # Verify that at least the valid source URL is extracted
        assert mock_source in result_state["link_urls"]