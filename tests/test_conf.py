import os
import sys
import unittest

from docs.source import conf

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the conf module

class TestSphinxConfig(unittest.TestCase):
    def test_sphinx_configuration(self):
        # Test project information
        self.assertEqual(conf.project, "ScrapeGraphAI")
        self.assertEqual(conf.copyright, "2024, ScrapeGraphAI")
        self.assertEqual(conf.author, "Marco Vinciguerra, Marco Perini, Lorenzo Padoan")

        # Test general configuration
        self.assertIn("sphinx.ext.autodoc", conf.extensions)
        self.assertIn("sphinx.ext.napoleon", conf.extensions)
        self.assertEqual(conf.templates_path, ["_templates"])
        self.assertEqual(conf.exclude_patterns, [])

        # Test HTML output configuration
        self.assertEqual(conf.html_theme, "furo")
        self.assertIsInstance(conf.html_theme_options, dict)
        self.assertEqual(conf.html_theme_options["source_repository"], 
                         "https://github.com/VinciGit00/Scrapegraph-ai/")
        self.assertEqual(conf.html_theme_options["source_branch"], "main")
        self.assertEqual(conf.html_theme_options["source_directory"], "docs/source/")
        self.assertTrue(conf.html_theme_options["navigation_with_keys"])
        self.assertFalse(conf.html_theme_options["sidebar_hide_name"])

if __name__ == '__main__':
    unittest.main()