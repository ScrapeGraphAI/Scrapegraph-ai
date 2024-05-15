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

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon','sphinx_wagtail_theme']

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'sphinx_rtd_theme'
html_theme = 'sphinx_wagtail_theme'

html_theme_options = dict(
    project_name = "ScrapeGraphAI",
    logo = "scrapegraphai_logo.png",
    logo_alt = "ScrapeGraphAI",
    logo_height = 59,
    logo_url = "https://scrapegraph-ai.readthedocs.io/en/latest/",
    logo_width = 45,
    github_url = "https://github.com/VinciGit00/Scrapegraph-ai/tree/main/docs/source/",
    footer_links = ",".join(
        ["Landing Page|https://scrapegraphai.com/",
         "Docusaurus|https://scrapegraph-doc.onrender.com/docs/intro"]
         ),
)
