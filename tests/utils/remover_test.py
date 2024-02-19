""" 
Test for the remover method
"""
import unittest

from scrapegraphai.utils.remover import remover


class TestRemover(unittest.TestCase):
    """Test class """

    def test_remover_basic(self):
        """First test"""
        html_content = """
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>This is a Test</h1>
            <p>Hello, World!</p>
            <script>alert("This is a script");</script>
        </body>
        </html>
        """
        expected_result = """<title>Test Page</title>
        <body><h1>This is a Test</h1><p>Hello, World!</p></body>"""
        self.assertEqual(remover(html_content), expected_result)

    def test_remover_only_body(self):
        """Second test"""
        html_content = """
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1>This is a Test</h1>
            <p>Hello, World!</p>
            <script>alert("This is a script");</script>
        </body>
        </html>
        """
        expected_result = '<h1>This is a Test</h1><p>Hello, World!</p>'
        self.assertEqual(
            remover(html_content, only_body=True), expected_result)

    def test_remover_no_body(self):
        """Third test"""
        html_content = """
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <p>This is a paragraph.</p>
        </html>
        """
        expected_result = '<title>Test Page</title>'
        self.assertEqual(remover(html_content), expected_result)


if __name__ == '__main__':
    unittest.main()
