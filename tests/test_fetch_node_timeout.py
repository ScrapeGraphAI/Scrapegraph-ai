"""
Unit tests for FetchNode timeout functionality.

These tests verify that:
1. The timeout configuration is properly read and stored
2. HTTP requests use the configured timeout
3. PDF parsing respects the timeout
4. Timeout is propagated to ChromiumLoader via loader_kwargs
"""
import sys
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add the project root to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestFetchNodeTimeout(unittest.TestCase):
    """Test suite for FetchNode timeout configuration and usage."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock all the heavy external dependencies at import time
        self.mock_modules = {}
        for module in ['langchain_core', 'langchain_core.documents',
                       'langchain_community', 'langchain_community.document_loaders',
                       'langchain_openai', 'minify_html', 'pydantic',
                       'langchain', 'langchain.prompts']:
            if module not in sys.modules:
                sys.modules[module] = MagicMock()

        # Create mock Document class
        class MockDocument:
            def __init__(self, page_content, metadata=None):
                self.page_content = page_content
                self.metadata = metadata or {}

        sys.modules['langchain_core.documents'].Document = MockDocument

        # Create mock PyPDFLoader
        class MockPyPDFLoader:
            def __init__(self, source):
                self.source = source

            def load(self):
                time.sleep(0.1)  # Simulate some work
                return [MockDocument(page_content=f"PDF content from {self.source}")]

        sys.modules['langchain_community.document_loaders'].PyPDFLoader = MockPyPDFLoader

        # Now import FetchNode
        from scrapegraphai.nodes.fetch_node import FetchNode
        self.FetchNode = FetchNode

    def tearDown(self):
        """Clean up after tests."""
        # Remove mocked modules
        for module in list(sys.modules.keys()):
            if 'langchain' in module or module in ['minify_html', 'pydantic']:
                if module in self.mock_modules or module.startswith('langchain'):
                    sys.modules.pop(module, None)

    def test_timeout_default_value(self):
        """Test that default timeout is set to 30 seconds."""
        node = self.FetchNode(
            input="url",
            output=["doc"],
            node_config={}
        )
        self.assertEqual(node.timeout, 30)

    def test_timeout_custom_value(self):
        """Test that custom timeout value is properly stored."""
        node = self.FetchNode(
            input="url",
            output=["doc"],
            node_config={"timeout": 10}
        )
        self.assertEqual(node.timeout, 10)

    def test_timeout_none_value(self):
        """Test that timeout can be disabled by setting to None."""
        node = self.FetchNode(
            input="url",
            output=["doc"],
            node_config={"timeout": None}
        )
        self.assertIsNone(node.timeout)

    def test_timeout_no_config(self):
        """Test that timeout defaults to 30 when no node_config provided."""
        node = self.FetchNode(
            input="url",
            output=["doc"],
            node_config=None
        )
        self.assertEqual(node.timeout, 30)

    @patch('scrapegraphai.nodes.fetch_node.requests')
    def test_requests_get_with_timeout(self, mock_requests):
        """Test that requests.get is called with timeout when use_soup=True."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_requests.get.return_value = mock_response

        node = self.FetchNode(
            input="url",
            output=["doc"],
            node_config={"use_soup": True, "timeout": 15}
        )

        # Execute with a URL
        state = {"url": "https://example.com"}
        node.execute(state)

        # Verify requests.get was called with timeout
        mock_requests.get.assert_called_once()
        call_args = mock_requests.get.call_args
        self.assertEqual(call_args[1].get('timeout'), 15)

    @patch('scrapegraphai.nodes.fetch_node.requests')
    def test_requests_get_without_timeout_when_none(self, mock_requests):
        """Test that requests.get is called without timeout argument when timeout=None."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test content</body></html>"
        mock_requests.get.return_value = mock_response

        node = self.FetchNode(
            input="url",
            output=["doc"],
            node_config={"use_soup": True, "timeout": None}
        )

        # Execute with a URL
        state = {"url": "https://example.com"}
        node.execute(state)

        # Verify requests.get was called without timeout
        mock_requests.get.assert_called_once()
        call_args = mock_requests.get.call_args
        self.assertNotIn('timeout', call_args[1])

    def test_pdf_parsing_with_timeout(self):
        """Test that PDF parsing completes within timeout."""
        node = self.FetchNode(
            input="pdf",
            output=["doc"],
            node_config={"timeout": 5}
        )

        # Execute with a PDF file
        state = {"pdf": "test.pdf"}
        result = node.execute(state)

        # Should complete successfully
        self.assertIn("doc", result)
        self.assertIsNotNone(result["doc"])

    def test_pdf_parsing_timeout_exceeded(self):
        """Test that PDF parsing raises TimeoutError when timeout is exceeded."""
        # Create a mock loader that takes longer than timeout
        class SlowPyPDFLoader:
            def __init__(self, source):
                self.source = source

            def load(self):
                time.sleep(2)  # Sleep longer than timeout
                return []

        with patch('scrapegraphai.nodes.fetch_node.PyPDFLoader', SlowPyPDFLoader):
            node = self.FetchNode(
                input="pdf",
                output=["doc"],
                node_config={"timeout": 0.5}  # Very short timeout
            )

            # Execute should raise TimeoutError
            state = {"pdf": "slow.pdf"}
            with self.assertRaises(TimeoutError) as context:
                node.execute(state)

            self.assertIn("PDF parsing exceeded timeout", str(context.exception))

    @patch('scrapegraphai.nodes.fetch_node.ChromiumLoader')
    def test_timeout_propagated_to_chromium_loader(self, mock_loader_class):
        """Test that timeout is propagated to ChromiumLoader via loader_kwargs."""
        mock_loader = Mock()
        mock_doc = Mock()
        mock_doc.page_content = "<html>Test</html>"
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader

        node = self.FetchNode(
            input="url",
            output=["doc"],
            node_config={"timeout": 20, "headless": True}
        )

        # Execute with a URL (not using soup, so ChromiumLoader is used)
        state = {"url": "https://example.com"}
        node.execute(state)

        # Verify ChromiumLoader was instantiated with timeout in kwargs
        mock_loader_class.assert_called_once()
        call_kwargs = mock_loader_class.call_args[1]
        self.assertEqual(call_kwargs.get('timeout'), 20)

    @patch('scrapegraphai.nodes.fetch_node.ChromiumLoader')
    def test_timeout_not_overridden_in_loader_kwargs(self, mock_loader_class):
        """Test that existing timeout in loader_kwargs is not overridden."""
        mock_loader = Mock()
        mock_doc = Mock()
        mock_doc.page_content = "<html>Test</html>"
        mock_loader.load.return_value = [mock_doc]
        mock_loader_class.return_value = mock_loader

        node = self.FetchNode(
            input="url",
            output=["doc"],
            node_config={
                "timeout": 20,
                "loader_kwargs": {"timeout": 50}  # Explicit loader timeout
            }
        )

        # Execute with a URL
        state = {"url": "https://example.com"}
        node.execute(state)

        # Verify ChromiumLoader got the loader_kwargs timeout, not node timeout
        mock_loader_class.assert_called_once()
        call_kwargs = mock_loader_class.call_args[1]
        self.assertEqual(call_kwargs.get('timeout'), 50)


if __name__ == '__main__':
    unittest.main()
