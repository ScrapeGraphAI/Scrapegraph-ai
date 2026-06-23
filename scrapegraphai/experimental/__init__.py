"""
Experimental backends module.

Uses lazy __getattr__ to defer importing loaders until first use,
preventing torchcodec/FFmpeg DLL crashes at import time.
"""

_LAZY_MODULES = {
    "ObscuraLoader": ".obscura_loader",
    "Crawl4aiLoader": ".crawl4ai_loader",
    "CamoufoxLoader": ".camoufox_loader",
}


def __getattr__(name):
    if name in _LAZY_MODULES:
        import importlib
        module = importlib.import_module(_LAZY_MODULES[name], __package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ObscuraLoader",
    "Crawl4aiLoader",
    "CamoufoxLoader",
]
