"""
Adaptive Speaker Scraper

Intelligently detects website type and chooses optimal scraping strategy:
1. Pure HTML -> SmartScraperGraph (cheapest, text-only)
2. Mixed content -> OmniScraperGraph (processes images selectively)
3. Pure images -> ScreenshotScraperGraph (full page screenshot)

Usage:
    python adaptive_speaker_scraper.py
"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from scrapegraphai.graphs import (
    OmniScraperGraph,
    ScreenshotScraperGraph,
    SmartScraperGraph,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")


class WebsiteType(Enum):
    """Classification of website content types."""

    PURE_HTML = "pure_html"  # All data in HTML text
    MIXED_CONTENT = "mixed_content"  # HTML text + images with data
    PURE_IMAGES = "pure_images"  # Data only in images


class Speaker(BaseModel):
    """Schema for a single speaker entry."""

    first_name: str = Field(default="")
    last_name: str = Field(default="")
    full_name: str = Field(default="")
    company: str = Field(default="")
    position: str = Field(default="")
    linkedin_url: str = Field(default="")


class EventInfo(BaseModel):
    """Schema for event metadata."""

    event_name: str = Field(default="")
    event_dates: str = Field(default="")
    event_location: str = Field(default="")
    event_time: str = Field(default="")


class SpeakerScrapeResult(BaseModel):
    """Overall schema for scraping results."""

    event: EventInfo = Field(default_factory=EventInfo)
    speakers: List[Speaker] = Field(default_factory=list)


def calculate_completeness_score(result: dict) -> float:
    """
    Calculate how complete the extracted data is (0.0 to 1.0).

    Args:
        result: Scraping result dictionary

    Returns:
        Completeness score: 1.0 = perfect, 0.0 = empty
    """
    speakers = result.get("speakers", [])

    if not speakers:
        return 0.0

    total_fields = 0
    filled_fields = 0

    # Core fields we care about
    important_fields = ["full_name", "company", "position"]

    for speaker in speakers:
        for field in important_fields:
            total_fields += 1
            value = speaker.get(field, "").strip()
            if value and value.lower() not in ["", "na", "n/a", "null", "none"]:
                filled_fields += 1

    return filled_fields / total_fields if total_fields > 0 else 0.0


def count_images_in_state(graph) -> int:
    """
    Count how many images were found on the page.

    Args:
        graph: The scraper graph instance

    Returns:
        Number of images found
    """
    try:
        state = graph.get_state() if hasattr(graph, 'get_state') else {}
        img_urls = state.get("img_urls", [])
        return len(img_urls) if img_urls else 0
    except Exception:
        return 0


def detect_website_type(
    url: str,
    prompt: str,
    config: dict,
    schema: type[BaseModel],
) -> Tuple[WebsiteType, dict, dict]:
    """
    Intelligently detect website type by running SmartScraperGraph first.

    Strategy:
    1. Try SmartScraperGraph (cheapest)
    2. Analyze completeness and image count
    3. Classify as PURE_HTML, MIXED_CONTENT, or PURE_IMAGES

    Args:
        url: Website URL
        prompt: Extraction prompt
        config: Graph configuration
        schema: Pydantic schema for results

    Returns:
        Tuple of (website_type, initial_result, analysis_info)
    """
    print(f"\n🔍 Analyzing website: {url}")
    print("📊 Running initial SmartScraperGraph analysis...")

    # Step 1: Try text-based extraction
    smart_graph = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=config,
        schema=schema,
    )

    result = smart_graph.run()

    # Step 2: Analyze results
    completeness = calculate_completeness_score(result)
    num_images = count_images_in_state(smart_graph)
    num_speakers = len(result.get("speakers", []))

    analysis = {
        "completeness_score": completeness,
        "num_speakers_found": num_speakers,
        "num_images_detected": num_images,
    }

    print(f"   ✓ Completeness: {completeness:.1%}")
    print(f"   ✓ Speakers found: {num_speakers}")
    print(f"   ✓ Images detected: {num_images}")

    # Step 3: Classify website type
    if completeness >= 0.8:
        # High completeness -> Pure HTML
        website_type = WebsiteType.PURE_HTML
        print("   → Classification: PURE_HTML ✅ (Using SmartScraperGraph)")

    elif completeness >= 0.5 and num_images > num_speakers * 0.5:
        # Medium-high completeness + many images -> Mixed content
        website_type = WebsiteType.MIXED_CONTENT
        print("   → Classification: MIXED_CONTENT 🔄 (Will use OmniScraperGraph)")

    elif completeness < 0.5:
        # Low completeness (<50%) -> Try screenshot approach
        # This catches cases where data is in images/background/canvas
        website_type = WebsiteType.PURE_IMAGES
        print("   → Classification: PURE_IMAGES 📸 (Will use ScreenshotScraperGraph)")
        print("   ℹ️  Reason: Low data completeness suggests info is in images")

    else:
        # Default to screenshot for safety when uncertain
        website_type = WebsiteType.PURE_IMAGES
        print("   → Classification: PURE_IMAGES (fallback, using screenshot approach)")

    return website_type, result, analysis


def scrape_with_optimal_strategy(
    url: str,
    prompt: str,
    config: dict,
    schema: type[BaseModel],
) -> dict:
    """
    Automatically detect website type and use optimal scraping strategy.

    Args:
        url: Website URL
        prompt: Extraction prompt
        config: Graph configuration
        schema: Pydantic schema

    Returns:
        Scraping results with metadata
    """
    # Detect website type
    website_type, initial_result, analysis = detect_website_type(
        url, prompt, config, schema
    )

    # Apply optimal strategy
    if website_type == WebsiteType.PURE_HTML:
        # Already have good results from SmartScraperGraph
        final_result = initial_result
        strategy = "SmartScraperGraph"

    elif website_type == WebsiteType.MIXED_CONTENT:
        # Use OmniScraperGraph for hybrid extraction
        print("\n🔄 Re-scraping with OmniScraperGraph for image data...")
        omni_config = config.copy()
        omni_config["max_images"] = min(
            analysis.get("num_images_detected", 10), 50
        )

        omni_graph = OmniScraperGraph(
            prompt=prompt,
            source=url,
            config=omni_config,
            schema=schema,
        )
        final_result = omni_graph.run()
        strategy = "OmniScraperGraph"

    else:  # PURE_IMAGES
        # Use ScreenshotScraperGraph for full page capture
        print("\n📸 Scraping with ScreenshotScraperGraph (full page screenshots)...")
        screenshot_graph = ScreenshotScraperGraph(
            prompt=prompt,
            source=url,
            config=config,
            schema=schema,
        )
        final_result = screenshot_graph.run()
        strategy = "ScreenshotScraperGraph"

        # Fallback: If screenshot failed, use initial SmartScraperGraph result
        screenshot_speakers = final_result.get("speakers", []) if isinstance(final_result, dict) else []
        if len(screenshot_speakers) == 0 and len(initial_result.get("speakers", [])) > 0:
            print("   ⚠️  Screenshot extraction failed, using SmartScraperGraph result")
            final_result = initial_result
            strategy = "SmartScraperGraph (screenshot fallback)"

    # Add metadata
    return {
        "url": url,
        "website_type": website_type.value,
        "strategy_used": strategy,
        "analysis": analysis,
        "data": final_result,
    }


def main():
    """Demonstrate adaptive scraping on different website types."""

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not found in environment")

    # Configuration
    config = {
        "llm": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "openai/gpt-4o",  # Vision model required for screenshots/images
            "temperature": 0,
        },
        "verbose": True,
        "headless": True,
    }

    prompt = """
    Extract all speakers from this event page.
    For each speaker, capture:
      - first_name, last_name, full_name
      - company, position
      - linkedin_url (if available)

    Also capture event metadata:
      - event_name, event_dates, event_location, event_time

    Return structured JSON with all speakers found.
    """

    # Test URLs (add your own)
    test_urls = [
        "https://conferenziaworld.com/client-experience-conference/",
        # Add more URLs to test different types
    ]

    results = []

    for url in test_urls:
        print("\n" + "=" * 80)
        result = scrape_with_optimal_strategy(
            url=url,
            prompt=prompt,
            config=config,
            schema=SpeakerScrapeResult,
        )
        results.append(result)

        print(f"\n✅ Completed: {url}")
        print(f"   Strategy: {result['strategy_used']}")
        print(f"   Speakers extracted: {len(result['data'].get('speakers', []))}")

    # Save results
    output_path = Path(__file__).parent / "adaptive_scrape_results.json"
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n💾 Results saved to: {output_path}")


if __name__ == "__main__":
    main()
