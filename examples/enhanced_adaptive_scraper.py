"""
Enhanced Adaptive Speaker Scraper with Multi-Level Enrichment

This scraper uses a 3-level strategy:
1. Level 1: Extract from main page (HTML → SmartScraper, Images → Screenshot)
2. Level 2: Enrich from LinkedIn profiles if available
3. Level 3: Try individual speaker detail pages if they exist

Guarantees maximum data completeness while being cost-effective.
"""

import json
import os
from pathlib import Path
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from scrapegraphai.graphs import (
    OmniScraperGraph,
    ScreenshotScraperGraph,
    SmartScraperGraph,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")


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


def calculate_completeness(speakers: List[dict]) -> float:
    """Calculate completeness score for speaker data."""
    if not speakers:
        return 0.0

    total_fields = 0
    filled_fields = 0

    for speaker in speakers:
        for field in ["full_name", "company", "position"]:
            total_fields += 1
            value = speaker.get(field, "").strip()
            if value and value.lower() not in ["", "na", "n/a", "null", "none"]:
                filled_fields += 1

    return filled_fields / total_fields if total_fields > 0 else 0.0


def parse_screenshot_result(screenshot_result: dict, schema: type[BaseModel]) -> dict:
    """
    Parse ScreenshotScraperGraph result which returns {'consolidated_analysis': '...'}.

    The consolidated_analysis contains JSON (often wrapped in markdown code blocks).
    We need to extract and parse this JSON into our schema format.
    """
    import re

    # Get the raw text from consolidated_analysis
    consolidated_text = screenshot_result.get("consolidated_analysis", "")

    if not consolidated_text:
        return {"event": {}, "speakers": []}

    # Extract JSON from markdown code blocks - support both objects {...} and arrays [...]
    json_blocks = re.findall(r'```json\s*([\[\{].*?[\]\}])\s*```', consolidated_text, re.DOTALL)

    if not json_blocks:
        # Try to find JSON without code blocks - objects or arrays
        json_blocks = re.findall(r'([\[\{].*?[\]\}])', consolidated_text, re.DOTALL)

    if not json_blocks:
        print(f"   ⚠️  Could not extract JSON from screenshot result")
        return {"event": {}, "speakers": []}

    # Parse all JSON blocks and merge speakers
    all_speakers = []
    event_info = {}

    for json_str in json_blocks:
        try:
            data = json.loads(json_str)

            # Handle if data is a list (array of speakers)
            if isinstance(data, list):
                for speaker in data:
                    if isinstance(speaker, str):
                        # Simple string format: "Name"
                        all_speakers.append({
                            "full_name": speaker,
                            "first_name": speaker.split()[0] if speaker else "",
                            "last_name": " ".join(speaker.split()[1:]) if len(speaker.split()) > 1 else "",
                            "company": "",
                            "position": "",
                            "linkedin_url": "",
                        })
                    elif isinstance(speaker, dict):
                        # Dict format - normalize to our schema
                        all_speakers.append({
                            "full_name": speaker.get("name", speaker.get("full_name", "")),
                            "first_name": speaker.get("first_name", ""),
                            "last_name": speaker.get("last_name", ""),
                            "company": speaker.get("company") or "",
                            "position": speaker.get("position", speaker.get("title", "")),
                            "linkedin_url": speaker.get("linkedin_url") or "",
                        })

            # Handle if data is an object (dict)
            elif isinstance(data, dict):
                # Extract speakers from this block
                if "speakers" in data:
                    speakers = data["speakers"]

                    # Handle different formats
                    if isinstance(speakers, list):
                        for speaker in speakers:
                            if isinstance(speaker, str):
                                # Simple string format: "Name"
                                all_speakers.append({
                                    "full_name": speaker,
                                    "first_name": speaker.split()[0] if speaker else "",
                                    "last_name": " ".join(speaker.split()[1:]) if len(speaker.split()) > 1 else "",
                                    "company": "",
                                    "position": "",
                                    "linkedin_url": "",
                                })
                            elif isinstance(speaker, dict):
                                # Dict format - normalize to our schema
                                all_speakers.append({
                                    "full_name": speaker.get("name", speaker.get("full_name", "")),
                                    "first_name": speaker.get("first_name", ""),
                                    "last_name": speaker.get("last_name", ""),
                                    "company": speaker.get("company") or "",
                                    "position": speaker.get("position", speaker.get("title", "")),
                                    "linkedin_url": speaker.get("linkedin_url") or "",
                                })

                # Extract event info if present
                if "event" in data:
                    event_info = data["event"]
                elif "event_name" in data:
                    event_info = {
                        "event_name": data.get("event_name", ""),
                        "event_dates": data.get("event_dates", ""),
                        "event_location": data.get("event_location", ""),
                        "event_time": data.get("event_time", ""),
                    }

        except json.JSONDecodeError as e:
            print(f"   ⚠️  Failed to parse JSON block: {e}")
            continue

    # Deduplicate speakers by full_name
    # Also filter out obvious hallucinations (generic names with no company)
    hallucination_patterns = [
        "Emma Johnson", "Ava Thompson", "Liam Carter", "Noah Mitchell",
        "John Smith", "Jane Doe", "Michael Brown", "Sarah Williams"
    ]

    unique_speakers = {}
    for speaker in all_speakers:
        full_name = speaker.get("full_name", "")
        if full_name:
            full_name = full_name.strip()

        # Skip empty names
        if not full_name:
            continue

        # Skip obvious hallucinations (generic names with no company)
        company = speaker.get("company") or ""
        if isinstance(company, str):
            company = company.strip()

        # Filter out hallucinations: generic names with no company or "NA" company
        if full_name in hallucination_patterns and (not company or company.upper() == "NA"):
            continue

        if full_name not in unique_speakers:
            unique_speakers[full_name] = speaker

    return {
        "event": event_info,
        "speakers": list(unique_speakers.values()),
    }


def extract_from_linkedin(linkedin_url: str, config: dict) -> Optional[dict]:
    """
    Extract company and position from LinkedIn profile.

    Note: This is a placeholder. Real LinkedIn scraping requires:
    - Authentication
    - Handling rate limits
    - Parsing profile structure
    """
    # TODO: Implement LinkedIn scraping
    # For now, return None to indicate not implemented
    return None


def enrich_speakers_with_linkedin(speakers: List[dict], config: dict) -> List[dict]:
    """
    Enrich speaker data by scraping their LinkedIn profiles.
    Only scrapes profiles for speakers missing company/position.
    """
    enriched_speakers = []

    for speaker in speakers:
        # Check if speaker needs enrichment
        needs_enrichment = (
            not speaker.get("company") or speaker.get("company") == "NA"
        ) or (
            not speaker.get("position") or speaker.get("position") == "NA"
        )

        if needs_enrichment and speaker.get("linkedin_url"):
            print(f"   → Enriching {speaker.get('full_name')} from LinkedIn...")
            linkedin_data = extract_from_linkedin(speaker["linkedin_url"], config)

            if linkedin_data:
                speaker["company"] = linkedin_data.get("company", speaker.get("company"))
                speaker["position"] = linkedin_data.get("position", speaker.get("position"))

        enriched_speakers.append(speaker)

    return enriched_speakers


def scrape_with_enhanced_strategy(
    url: str,
    prompt: str,
    config: dict,
    schema: type[BaseModel],
    enable_linkedin_enrichment: bool = False,
) -> dict:
    """
    Enhanced adaptive scraping with multi-level data enrichment.

    Levels:
    1. Main page extraction (adaptive: Smart/Omni/Screenshot)
    2. LinkedIn enrichment (optional, for missing data)
    3. Individual page scraping (future enhancement)

    Args:
        url: Event page URL
        prompt: Extraction prompt
        config: Graph configuration
        schema: Pydantic schema
        enable_linkedin_enrichment: Whether to enrich from LinkedIn

    Returns:
        Complete scraping result with metadata
    """
    print(f"\n{'='*80}")
    print(f"🎯 Enhanced Adaptive Scraper")
    print(f"{'='*80}")
    print(f"URL: {url}")
    print(f"LinkedIn Enrichment: {'✅ Enabled' if enable_linkedin_enrichment else '❌ Disabled'}")

    # LEVEL 1: Main page extraction (adaptive)
    print(f"\n📊 LEVEL 1: Adaptive Main Page Extraction")
    print("-" * 80)

    # Try SmartScraperGraph first
    print("🔍 Trying SmartScraperGraph (text-based)...")
    smart_graph = SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=config,
        schema=schema,
    )
    result = smart_graph.run()

    completeness = calculate_completeness(result.get("speakers", []))
    num_speakers = len(result.get("speakers", []))

    print(f"   ✓ Found: {num_speakers} speakers")
    print(f"   ✓ Completeness: {completeness:.1%}")

    strategy_used = "SmartScraperGraph"

    # Decide if we need vision-based extraction
    # Use 80% threshold to catch cases where data is partially in images
    if completeness < 0.8:
        print(f"\n📸 Completeness < 80% ({completeness:.1%}), trying ScreenshotScraperGraph...")

        screenshot_graph = ScreenshotScraperGraph(
            prompt=prompt,
            source=url,
            config=config,
            schema=schema,
        )
        screenshot_result = screenshot_graph.run()

        # Parse the screenshot result - it returns {'consolidated_analysis': '...'}
        # We need to extract the JSON from the text
        screenshot_parsed = parse_screenshot_result(screenshot_result, schema)

        # Check if screenshot extraction worked better
        screenshot_speakers = screenshot_parsed.get("speakers", []) if isinstance(screenshot_parsed, dict) else []
        screenshot_completeness = calculate_completeness(screenshot_speakers)

        print(f"   ✓ Screenshot found: {len(screenshot_speakers)} speakers")
        print(f"   ✓ Screenshot completeness: {screenshot_completeness:.1%}")

        # Merge both results to get maximum coverage
        # SmartScraperGraph often catches hero/top speakers that screenshots miss
        # ScreenshotScraperGraph catches image-based speakers that HTML misses
        smart_speakers = result.get("speakers", [])
        screenshot_speakers_list = screenshot_parsed.get("speakers", [])

        # Combine speakers from both sources
        combined_speakers = {}

        # Add SmartScraper results first
        for speaker in smart_speakers:
            full_name = speaker.get("full_name", "").strip()
            if full_name:
                combined_speakers[full_name] = speaker

        # Add Screenshot results (won't duplicate due to dict key)
        for speaker in screenshot_speakers_list:
            full_name = speaker.get("full_name", "").strip()
            if full_name:
                # Prefer screenshot data if it has more complete info
                if full_name not in combined_speakers or calculate_completeness([speaker]) > calculate_completeness([combined_speakers[full_name]]):
                    combined_speakers[full_name] = speaker

        # Create merged result
        merged_result = {
            "event": result.get("event", screenshot_parsed.get("event", {})),
            "speakers": list(combined_speakers.values())
        }

        merged_count = len(merged_result["speakers"])
        merged_completeness = calculate_completeness(merged_result["speakers"])

        print(f"   → Merged results: {merged_count} speakers ({merged_completeness:.1%} completeness)")
        print(f"     (SmartScraper: {num_speakers}, Screenshot: {len(screenshot_speakers_list)})")

        result = merged_result
        strategy_used = "SmartScraperGraph + ScreenshotScraperGraph (Merged)"
        completeness = merged_completeness

    # LEVEL 2: LinkedIn enrichment (optional)
    if enable_linkedin_enrichment and completeness < 0.8:
        print(f"\n🔗 LEVEL 2: LinkedIn Profile Enrichment")
        print("-" * 80)

        speakers_with_linkedin = [
            s for s in result.get("speakers", [])
            if s.get("linkedin_url")
        ]

        if speakers_with_linkedin:
            print(f"Found {len(speakers_with_linkedin)} speakers with LinkedIn URLs")
            print("⚠️  LinkedIn enrichment not yet implemented (requires auth)")
            # result["speakers"] = enrich_speakers_with_linkedin(
            #     result["speakers"], config
            # )
        else:
            print("⚠️  No LinkedIn URLs found, skipping enrichment")

    # LEVEL 3: Individual page scraping (future)
    # TODO: Detect and scrape individual speaker detail pages

    # Final summary
    final_completeness = calculate_completeness(result.get("speakers", []))
    final_speakers = len(result.get("speakers", []))

    print(f"\n{'='*80}")
    print(f"✅ FINAL RESULTS")
    print(f"{'='*80}")
    print(f"Strategy: {strategy_used}")
    print(f"Speakers: {final_speakers}")
    print(f"Completeness: {final_completeness:.1%}")
    print(f"{'='*80}\n")

    return {
        "url": url,
        "strategy_used": strategy_used,
        "completeness_score": final_completeness,
        "speaker_count": final_speakers,
        "linkedin_enrichment_enabled": enable_linkedin_enrichment,
        "data": result,
    }


def main():
    """Test enhanced adaptive scraper."""
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY not found")

    config = {
        "llm": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "openai/gpt-4o",
            "temperature": 0,
            "max_tokens": 4000,  # Increased for screenshot extraction
        },
        "verbose": False,
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

    # Test URLs
    test_cases = [
        {
            "url": "https://conferenziaworld.com/client-experience-conference/",
            "description": "Mixed content - has names but company/position in images or missing",
        },
        {
            "url": "https://vds.tech/speakers/",
            "description": "Pure HTML - complete data in HTML",
        },
    ]

    results = []

    for test_case in test_cases:
        print(f"\n\n🧪 TEST CASE: {test_case['description']}")

        result = scrape_with_enhanced_strategy(
            url=test_case["url"],
            prompt=prompt,
            config=config,
            schema=SpeakerScrapeResult,
            enable_linkedin_enrichment=False,  # Set True when implemented
        )

        results.append(result)

    # Save results
    output_path = Path(__file__).parent / "enhanced_scrape_results.json"
    output_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n💾 Results saved to: {output_path}")


if __name__ == "__main__":
    main()
