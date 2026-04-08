"""
This module handles document loading functionalities for the ScrapeGraphAI application.
"""

from .browser_base import browser_base_fetch
from .chromium import ChromiumLoader
from .plasmate import PlasmateLoader
from .scrape_do import scrape_do_fetch

__all__ = [
    "browser_base_fetch",
    "ChromiumLoader",
    "PlasmateLoader",
    "scrape_do_fetch",
]
