"""Job source registry."""

from __future__ import annotations

from .base import Source, make_client
from .gupy import GupySource
from .infojobs import InfoJobsSource
from .linkedin import LinkedInSource
from .programathor import ProgramathorSource
from .sgai import ScrapeGraphSource
from .vagascom import VagasComSource

# Deterministic HTML/JSON sources. Fast and free.
CORE_SOURCES: dict[str, type] = {
    "gupy": GupySource,
    "linkedin": LinkedInSource,
    "programathor": ProgramathorSource,
    "infojobs": InfoJobsSource,
    "vagascom": VagasComSource,
}

# LLM-backed sources (ScrapeGraphAI + Playwright). Need an API key.
LLM_SOURCES: dict[str, type] = {
    "sgai": ScrapeGraphSource,
}

ALL_SOURCES: dict[str, type] = {**CORE_SOURCES, **LLM_SOURCES}


def build(names: list[str]) -> list[Source]:
    """Instantiate sources by name (``all`` / ``core`` / ``llm`` accepted)."""
    out: list[Source] = []
    for n in names:
        n = n.strip().lower()
        if n == "all":
            out.extend(cls() for cls in ALL_SOURCES.values())
        elif n == "core":
            out.extend(cls() for cls in CORE_SOURCES.values())
        elif n == "llm":
            out.extend(cls() for cls in LLM_SOURCES.values())
        elif n in ALL_SOURCES:
            out.append(ALL_SOURCES[n]())
        else:
            raise ValueError(f"unknown source {n!r}; options: {', '.join(ALL_SOURCES)}")
    # keep order, drop duplicates
    seen: set[str] = set()
    uniq: list[Source] = []
    for s in out:
        if s.name not in seen:
            seen.add(s.name)
            uniq.append(s)
    return uniq


__all__ = [
    "ALL_SOURCES",
    "CORE_SOURCES",
    "LLM_SOURCES",
    "Source",
    "build",
    "make_client",
]
