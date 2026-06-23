"""
This module handles document loading functionalities for the ScrapeGraphAI application.

Note: ChromiumLoader and PlasmateLoader are lazy-imported to avoid triggering
torchcodec/FFmpeg DLL loading at import time through the langchain import chain.
"""

from .browser_base import browser_base_fetch
from .scrape_do import scrape_do_fetch

_LAZY_MODULES = {
    "ChromiumLoader": ".chromium",
    "PlasmateLoader": ".plasmate",
}


def __getattr__(name):
    if name in _LAZY_MODULES:
        import importlib
        module = importlib.import_module(_LAZY_MODULES[name], __package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "browser_base_fetch",
    "ChromiumLoader",
    "PlasmateLoader",
    "scrape_do_fetch",
]
