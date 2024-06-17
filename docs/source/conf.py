# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# -- Path setup --------------------------------------------------------------

import os
import sys

# import all the modules
sys.path.insert(0, os.path.abspath('../../'))

project = 'ScrapeGraphAI'
copyright = '2024, ScrapeGraphAI'
author = 'Marco Vinciguerra, Marco Perini, Lorenzo Padoan'

html_last_updated_fmt = "%b %d, %Y"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_theme_options = {
    "source_repository": "https://github.com/VinciGit00/Scrapegraph-ai/",
    "source_branch": "main",
    "source_directory": "docs/source/",
    'navigation_with_keys': True,
    'sidebar_hide_name': False,
}

