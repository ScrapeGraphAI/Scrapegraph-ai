"""
Scrape Valencia Digital Summit speakers and event metadata with SmartScraperGraph.
"""

import json
import os
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from scrapegraphai.graphs import SmartScraperGraph

OUTPUT_PATH = Path(__file__).resolve().parent / "vds_speakers.json"
ROOT_DIR = Path(__file__).resolve().parent.parent


class Speaker(BaseModel):
    """Target schema for an individual speaker."""

    first_name: str = Field(default="")
    last_name: str = Field(default="")
    full_name: str = Field(default="")
    company: str = Field(default="")
    position: str = Field(default="")
    linkedin_url: str = Field(default="")


class EventInfo(BaseModel):
    """Target schema for event metadata."""

    event_name: str = Field(default="")
    event_dates: str = Field(default="")
    event_location: str = Field(default="")
    event_time: str = Field(default="")


class VDSResult(BaseModel):
    """Overall schema for the scraped payload."""

    event: EventInfo = Field(default_factory=EventInfo)
    speakers: List[Speaker] = Field(default_factory=list)


def build_graph() -> SmartScraperGraph:
    """
    Configure a SmartScraperGraph tailored for the VDS speakers page.

    Returns:
        SmartScraperGraph: Ready-to-run graph instance.
    """

    graph_config = {
        "llm": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "openai/gpt-4o-mini",
            "max_retries": 3,
            "temperature": 0,
        },
        "verbose": True,
        "headless": True,
    }

    prompt = """
    Collect structured data about the Valencia Digital Summit speakers from this page.
    For each speaker you find, capture:
      - first_name
      - last_name
      - full_name
      - company
      - position
      - linkedin_url (leave as empty string if not available)

    Also capture event metadata available on the page:
      - event_name
      - event_dates
      - event_location
      - event_time (leave empty string if no specific time is provided)

    Return a JSON object with:
      {
        "event": {
          "event_name": ...,
          "event_dates": ...,
          "event_location": ...,
          "event_time": ...
        },
        "speakers": [
          {
            "first_name": ...,
            "last_name": ...,
            "full_name": ...,
            "company": ...,
            "position": ...,
            "linkedin_url": ...
          }
        ]
      }
    """

    return SmartScraperGraph(
        prompt=prompt,
        source="https://vds.tech/speakers/",
        config=graph_config,
        schema=VDSResult,
    )


def main() -> None:
    """Execute the graph and persist the scraped results to disk."""
    load_dotenv(dotenv_path=ROOT_DIR / ".env")

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY not found. Make sure it is set in the environment or .env file."
        )

    graph = build_graph()
    result = graph.run()

    OUTPUT_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"Saved {len(result.get('speakers', []))} speakers to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
