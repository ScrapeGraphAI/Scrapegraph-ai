"""
Streamlit frontend to batch-scrape speaker information from multiple event pages.

Usage:
    streamlit run examples/frontend/batch_speaker_app.py

The app expects an ``OPENAI_API_KEY`` in the environment or in the project ``.env``.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from scrapegraphai.graphs import OmniScraperGraph, ScreenshotScraperGraph, SmartScraperGraph

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"

# Load environment variables once the module is imported
load_dotenv(ENV_PATH)

# Allow Streamlit secrets to provide API keys in hosted environments
try:
    secret_api_key = st.secrets.get("OPENAI_API_KEY")  # type: ignore[attr-defined]
    if secret_api_key:
        os.environ.setdefault("OPENAI_API_KEY", secret_api_key)
except Exception:
    pass


def ensure_playwright_installed() -> None:
    """Install Playwright browsers when running in ephemeral environments."""
    commands = [
        ["playwright", "install", "chromium"],
        ["playwright", "install", "--with-deps", "chromium"],
    ]
    last_error = ""
    for cmd in commands:
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return
        except FileNotFoundError:
            st.warning("Playwright CLI not found; please ensure Playwright is installed.", icon="⚠️")
            return
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8") if exc.stderr else ""
            if "already installed" in stderr.lower():
                return
            last_error = stderr
    if last_error:
        st.warning(f"Playwright install warning: {last_error}", icon="⚠️")


ensure_playwright_installed()


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
    """Overall schema for the SmartScraperGraph output."""

    event: EventInfo = Field(default_factory=EventInfo)
    speakers: List[Speaker] = Field(default_factory=list)


@dataclass
class ScrapeRun:
    """Session state bundle for a single scrape run."""

    url: str
    prompt: str
    success: bool
    used_ocr: bool = False
    fallback_triggered: bool = False
    used_omni: bool = False
    used_screenshot: bool = False
    auto_screenshot_triggered: bool = False
    ocr_transcripts: List[dict] = field(default_factory=list)
    screenshot_summary: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)
    error: str = ""


DEFAULT_PROMPT = """
Collect structured data about the event speakers on the supplied page.
For each speaker you find, capture:
  - first_name
  - last_name
  - full_name
  - company
  - position
  - linkedin_url (leave as empty string if not available)

If a speaker card primarily consists of an image, inspect the <img> alt text and any data/aria attributes
to glean company and position details. When the card presents a single combined line, keep it in position
and leave company empty; when multiple lines are present, treat the second as position and the third as the company.

Also capture event metadata visible on the page:
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

Prefer empty strings over null values when a field is missing.
""".strip()


def ensure_session_state() -> None:
    """Initialize the session state container used across reruns."""
    if "scrape_runs" not in st.session_state:
        st.session_state.scrape_runs: List[ScrapeRun] = []


def build_graph(
    url: str,
    prompt: str,
    model: str,
    headless: bool,
    loader_kwargs: dict,
    use_ocr: bool,
    max_images: int,
):
    """Create a graph instance for the supplied URL."""
    graph_config = {
        "llm": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": model,
            "max_retries": 3,
            "temperature": 0,
        },
        "headless": headless,
        "verbose": False,
    }

    if loader_kwargs:
        graph_config["loader_kwargs"] = loader_kwargs

    if use_ocr:
        graph_config["max_images"] = max_images
        return OmniScraperGraph(
            prompt=prompt,
            source=url,
            config=graph_config,
            schema=SpeakerScrapeResult,
        )

    return SmartScraperGraph(
        prompt=prompt,
        source=url,
        config=graph_config,
        schema=SpeakerScrapeResult,
    )


def needs_ocr_retry(result: dict) -> bool:
    """Heuristic: trigger OCR fallback if most speakers lack position/company."""
    speakers = result.get("speakers", [])
    if not speakers:
        return True

    missing = sum(
        1
        for speaker in speakers
        if not speaker.get("company") and not speaker.get("position")
    )

    return missing / len(speakers) >= 0.6


def should_use_omni(result: dict, image_metadata: List[dict]) -> bool:
    speakers = result.get("speakers", [])
    if not image_metadata:
        return False

    unique_images = {
        entry.get("url")
        for entry in image_metadata
        if entry.get("url")
    }

    if not unique_images:
        return False

    if not speakers:
        return True

    return len(speakers) < len(unique_images) * 0.6


def safe_get_state(graph) -> dict:
    """Return the latest graph state or an empty dict on failure."""
    try:
        return graph.get_state()
    except Exception:  # noqa: BLE001
        return {}


def is_vision_model(model: str) -> bool:
    """Check whether the selected model supports image inputs."""
    if not model:
        return False
    lower = model.lower()
    if any(term in lower for term in ("mini", "small", "tiny")):
        return False
    return any(keyword in lower for keyword in ("gpt-4o", "4o", "4.1", "4.5"))


def clean_model_name(model: str) -> str:
    """Strip provider prefix if present (e.g., openai/gpt-4o -> gpt-4o)."""
    if not model:
        return model
    return model.split("/", 1)[-1] if "/" in model else model


def build_omni_graph(
    url: str,
    prompt: str,
    model: str,
    headless: bool,
    loader_kwargs: dict,
    max_images: int,
) -> OmniScraperGraph:
    graph_config = {
        "llm": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": model,
            "max_retries": 3,
            "temperature": 0,
        },
        "headless": headless,
        "verbose": False,
        "max_images": max_images,
    }

    if loader_kwargs:
        graph_config["loader_kwargs"] = loader_kwargs

    return OmniScraperGraph(
        prompt=prompt,
        source=url,
        config=graph_config,
        schema=SpeakerScrapeResult,
    )


def normalize_text(value: str) -> str:
    """Lowercase, accent-strip, and remove punctuation for fuzzy matching."""
    if not value:
        return ""

    normalized = unicodedata.normalize("NFKD", value)
    cleaned = "".join(
        ch for ch in normalized if ch.isalnum() or ch.isspace()
    )
    return cleaned.lower().strip()


def collect_normalized_names(result: dict) -> List[str]:
    names = []
    for speaker in result.get("speakers", []):
        full = speaker.get("full_name") or ""
        first = speaker.get("first_name") or ""
        last = speaker.get("last_name") or ""

        for candidate in (full, f"{first} {last}".strip(), first, last):
            norm = normalize_text(candidate)
            if norm and norm not in names:
                names.append(norm)
    return names


def matches_speaker_image(entry: dict, names: List[str]) -> bool:
    if not names:
        return False

    alt_norm = normalize_text(entry.get("alt", ""))
    url = entry.get("url", "")
    stem_norm = ""
    if url:
        path = urlparse(url).path
        stem = Path(path).stem.replace("-", " ")
        stem_norm = normalize_text(stem)

    for name in names:
        if not name:
            continue
        if name in alt_norm or name in stem_norm:
            return True
    return False


def parse_screenshot_result(raw_answer: dict) -> dict:
    """Extract structured speaker data from ScreenshotScraperGraph output."""
    if not isinstance(raw_answer, dict):
        return {"event": {}, "speakers": []}

    consolidated_text = raw_answer.get("consolidated_analysis", "")
    if not consolidated_text:
        return {"event": {}, "speakers": []}

    json_blocks = re.findall(r"```json\s*([\[\{].*?[\]\}])\s*```", consolidated_text, re.DOTALL)
    if not json_blocks:
        json_blocks = re.findall(r"([\[\{].*?[\]\}])", consolidated_text, re.DOTALL)

    all_speakers: List[dict] = []
    event_info: dict = {}

    for block in json_blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue

        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    all_speakers.append(
                        ensure_schema(
                            {
                                "full_name": item,
                                "first_name": item.split()[0] if item else "",
                                "last_name": " ".join(item.split()[1:]) if len(item.split()) > 1 else "",
                            }
                        )
                    )
                elif isinstance(item, dict):
                    all_speakers.append(
                        ensure_schema(
                            {
                                "full_name": item.get("full_name") or item.get("name", ""),
                                "first_name": item.get("first_name", ""),
                                "last_name": item.get("last_name", ""),
                                "company": item.get("company") or "",
                                "position": item.get("position") or item.get("title", ""),
                                "linkedin_url": item.get("linkedin_url") or "",
                            }
                        )
                    )
        elif isinstance(data, dict):
            if "speakers" in data and isinstance(data["speakers"], list):
                for speaker in data["speakers"]:
                    if isinstance(speaker, str):
                        all_speakers.append(
                            ensure_schema(
                                {
                                    "full_name": speaker,
                                    "first_name": speaker.split()[0] if speaker else "",
                                    "last_name": " ".join(speaker.split()[1:]) if len(speaker.split()) > 1 else "",
                                }
                            )
                        )
                    elif isinstance(speaker, dict):
                        all_speakers.append(
                            ensure_schema(
                                {
                                    "full_name": speaker.get("full_name") or speaker.get("name", ""),
                                    "first_name": speaker.get("first_name", ""),
                                    "last_name": speaker.get("last_name", ""),
                                    "company": speaker.get("company") or "",
                                    "position": speaker.get("position") or speaker.get("title", ""),
                                    "linkedin_url": speaker.get("linkedin_url") or "",
                                }
                            )
                        )
            if "event" in data and isinstance(data["event"], dict):
                event_info = data["event"]
            elif any(key in data for key in ("event_name", "event_dates", "event_location", "event_time")):
                event_info = {
                    "event_name": data.get("event_name", ""),
                    "event_dates": data.get("event_dates", ""),
                    "event_location": data.get("event_location", ""),
                    "event_time": data.get("event_time", ""),
                }

    # Deduplicate by normalized full name
    unique: dict[str, dict] = {}
    for speaker in all_speakers:
        key = normalize_text(speaker.get("full_name", ""))
        if not key:
            continue
        unique.setdefault(key, speaker)

    return {"event": event_info, "speakers": list(unique.values())}


def speaker_completeness_score(speaker: dict) -> int:
    """Score speaker by how many key fields are populated."""
    score = 0
    for field_name in ("company", "position", "linkedin_url"):
        value = (speaker or {}).get(field_name, "")
        if isinstance(value, str) and value.strip():
            score += 1
    return score


def merge_with_screenshot_data(base: dict, screenshot_data: dict) -> dict:
    """Merge screenshot-derived speakers into the base result."""
    base = base or {}
    screenshot_data = screenshot_data or {}

    combined: dict[str, dict] = {}
    for speaker in base.get("speakers", []):
        key = normalize_text(speaker.get("full_name", ""))
        if not key:
            continue
        combined[key] = ensure_schema(speaker)

    for speaker in screenshot_data.get("speakers", []):
        key = normalize_text(speaker.get("full_name", ""))
        if not key:
            continue
        candidate = ensure_schema(speaker)
        if key not in combined or speaker_completeness_score(candidate) > speaker_completeness_score(combined[key]):
            combined[key] = candidate

    merged_event = base.get("event") or screenshot_data.get("event") or {}
    return {"event": merged_event, "speakers": list(combined.values())}


def should_trigger_screenshot(result: dict, image_entries: List[dict]) -> bool:
    """Heuristic to determine if screenshot fallback should run automatically."""
    speaker_count = len(result.get("speakers", []))
    if speaker_count == 0:
        return True

    if needs_ocr_retry(result):
        return True

    speaker_like_images = []
    for entry in image_entries:
        url_val = entry.get("url", "")
        alt_val = entry.get("alt", "")
        url_hit = isinstance(url_val, str) and "speaker" in url_val.lower()
        alt_hit = isinstance(alt_val, str) and "speaker" in alt_val.lower()
        if url_hit or alt_hit:
            speaker_like_images.append(entry)
    if len(speaker_like_images) >= 4:
        return True

    return False


def transcribe_images(
    image_entries: List[dict],
    model: str,
    api_key: str,
    max_images: int,
) -> List[dict]:
    """Use a vision-capable model to extract raw text from speaker images."""
    if not image_entries or not is_vision_model(model) or not api_key:
        return []

    chat = ChatOpenAI(
        model=clean_model_name(model),
        api_key=api_key,
        temperature=0,
        max_tokens=256,
    )

    transcripts: List[dict] = []
    for entry in image_entries[:max_images]:
        url = entry.get("url", "")
        alt_text = entry.get("alt", "")
        if not url:
            continue
        try:
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": (
                            "Transcribe every piece of text visible in this image. "
                            "If the image shows a speaker card, capture the name, job title, "
                            "and company exactly as written. Respond with plain text only."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": url, "detail": "high"},
                    },
                ]
            )
            text = chat.invoke([message]).content.strip()
        except Exception as exc:  # noqa: BLE001
            text = ""
            transcripts.append(
                {
                    "url": url,
                    "alt": alt_text,
                    "text": text,
                    "error": str(exc),
                }
            )
        else:
            transcripts.append({"url": url, "alt": alt_text, "text": text})
    return transcripts


def merge_result_with_transcripts(
    result: dict,
    transcripts: List[dict],
    user_prompt: str,
    model: str,
    api_key: str,
) -> dict:
    """Ask the LLM to fill gaps using OCR transcripts."""
    if not transcripts or not api_key:
        return result

    chat = ChatOpenAI(
        model=clean_model_name(model),
        api_key=api_key,
        temperature=0,
        max_tokens=1024,
    )

    system_msg = SystemMessage(
        content=(
            "You refine scraped speaker data. "
            "Use the provided OCR transcripts to fill missing company or position fields. "
            "If a transcript clearly describes a speaker not already in the JSON, append them, but avoid duplicates."
        )
    )
    user_msg = HumanMessage(
        content=(
            "User extraction prompt:\n"
            f"{user_prompt}\n\n"
            "Current scraped result JSON:\n"
            f"{json.dumps(result, ensure_ascii=False)}\n\n"
            "OCR transcripts extracted from speaker images:\n"
            f"{json.dumps(transcripts, ensure_ascii=False)}\n\n"
            "Return the updated JSON with the same structure. "
            "If OCR text does not contain the missing information, leave the fields empty."
        )
    )

    try:
        response = chat.invoke([system_msg, user_msg]).content
        updated = json.loads(response)
        if isinstance(updated, dict):
            return merge_structured_fields(result, updated)
    except Exception:  # noqa: BLE001
        return result

    return result


def merge_structured_fields(base: dict, updated: dict) -> dict:
    """Merge non-empty company/position fields from OCR output back into the base result."""
    base_speakers = base.get("speakers", [])
    updated_speakers = updated.get("speakers", [])

    if not base_speakers or not updated_speakers:
        return updated

    name_to_idx = {}
    existing_names = set()
    for idx, speaker in enumerate(base_speakers):
        full = normalize_text(speaker.get("full_name", ""))
        fallback = normalize_text(
            f"{speaker.get('first_name', '')} {speaker.get('last_name', '')}"
        )
        if full:
            name_to_idx[full] = idx
            existing_names.add(full)
        if fallback:
            name_to_idx.setdefault(fallback, idx)
            existing_names.add(fallback)

    for updated_speaker in updated_speakers:
        key = normalize_text(updated_speaker.get("full_name", ""))
        fallback = normalize_text(
            f"{updated_speaker.get('first_name', '')} {updated_speaker.get('last_name', '')}"
        )
        idx = name_to_idx.get(key) or name_to_idx.get(fallback)
        if idx is None:
            normalized_name = key or fallback
            if normalized_name and normalized_name not in existing_names:
                base_speakers.append(ensure_schema(updated_speaker))
                existing_names.add(normalized_name)
            continue

        target = base_speakers[idx]
        for field in ("company", "position"):
            value = updated_speaker.get(field)
            if value:
                target[field] = value

    base["speakers"] = base_speakers
    return base


def ensure_schema(speaker: dict) -> dict:
    return {
        "first_name": speaker.get("first_name", ""),
        "last_name": speaker.get("last_name", ""),
        "full_name": speaker.get("full_name", ""),
        "company": speaker.get("company", ""),
        "position": speaker.get("position", ""),
        "linkedin_url": speaker.get("linkedin_url", ""),
    }


def run_scraper(
    urls: List[str],
    prompt: str,
    model: str,
    headless: bool,
    loader_kwargs: dict,
    use_ocr: bool,
    max_images: int,
    omni_fallback: bool,
    screenshot_fallback: bool,
) -> None:
    """Execute the scraper for each URL and store the results in session state."""
    st.session_state.scrape_runs.clear()
    api_key = os.getenv("OPENAI_API_KEY", "")

    for idx, url in enumerate(urls, start=1):
        with st.spinner(f"Scraping {url} ({idx}/{len(urls)})"):
            try:
                current_use_ocr = use_ocr
                graph = build_graph(
                    url=url,
                    prompt=prompt,
                    model=model,
                    headless=headless,
                    loader_kwargs=loader_kwargs,
                    use_ocr=use_ocr,
                    max_images=max_images,
                )
                result = graph.run()
                state = safe_get_state(graph)

                img_metadata = state.get("img_metadata") or []
                img_urls = state.get("img_urls") or []
                image_entries_raw: List[dict] = list(img_metadata)
                if not image_entries_raw and img_urls:
                    image_entries_raw = [{"url": url, "alt": ""} for url in img_urls]

                fallback_triggered = False
                used_omni = use_ocr
                used_screenshot = False
                screenshot_summary: dict = {}
                auto_screenshot_triggered = False

                if omni_fallback and should_use_omni(result, img_metadata):
                    with st.spinner("Smart scrape incomplete; retrying with OmniScraperGraph..."):
                        omni_graph = build_omni_graph(
                            url=url,
                            prompt=prompt,
                            model=model,
                            headless=headless,
                            loader_kwargs=loader_kwargs,
                            max_images=max_images,
                        )
                        omni_result = omni_graph.run()
                        result = merge_structured_fields(result, omni_result)
                        omni_state = safe_get_state(omni_graph)
                        img_metadata = omni_state.get("img_metadata") or img_metadata
                        img_urls = omni_state.get("img_urls") or img_urls
                        used_omni = True
                        fallback_triggered = True
                        current_use_ocr = True

                transcripts: List[dict] = []
                if current_use_ocr and not used_omni:
                    image_entries = list(image_entries_raw)

                    noise_tokens = ("themes/", "assets/", "logo", "youtube", "giphy")
                    filtered = [
                        entry
                        for entry in image_entries
                        if entry.get("url")
                        and not any(token in entry["url"].lower() for token in noise_tokens)
                    ]
                    if filtered:
                        image_entries = filtered

                    speaker_names = collect_normalized_names(result)
                    if speaker_names:
                        name_matches = [
                            entry
                            for entry in image_entries
                            if matches_speaker_image(entry, speaker_names)
                        ]
                        if name_matches:
                            image_entries = name_matches

                    speaker_entries = [
                        entry
                        for entry in image_entries
                        if entry.get("alt")
                        and "speaker" in entry.get("alt", "").lower()
                    ]
                    if speaker_entries:
                        image_entries = speaker_entries

                    transcripts = transcribe_images(
                        image_entries=image_entries,
                        model=model,
                        api_key=api_key,
                        max_images=max_images,
                    )
                    if transcripts:
                        result = merge_result_with_transcripts(
                            result=result,
                            transcripts=transcripts,
                            user_prompt=prompt,
                            model=model,
                            api_key=api_key,
                        )

                auto_screenshot_needed = should_trigger_screenshot(result, image_entries_raw)
                run_screenshot_fallback = screenshot_fallback or auto_screenshot_needed

                if run_screenshot_fallback:
                    if not is_vision_model(model):
                        st.warning(
                            "Screenshot fallback skipped because the selected model lacks vision support.",
                            icon="⚠️",
                        )
                    elif not api_key:
                        st.warning("Screenshot fallback skipped: missing OPENAI_API_KEY.", icon="⚠️")
                    else:
                        with st.spinner("Running ScreenshotScraperGraph fallback..."):
                            screenshot_config = {
                                "llm": {
                                    "api_key": api_key,
                                    "model": model,
                                    "temperature": 0,
                                    "max_tokens": 4000,
                                },
                                "headless": headless,
                                "verbose": False,
                            }
                            try:
                                screenshot_graph = ScreenshotScraperGraph(
                                    prompt=prompt,
                                    source=url,
                                    config=screenshot_config,
                                    schema=SpeakerScrapeResult,
                                )
                                screenshot_raw = screenshot_graph.run()
                                raw_dict = (
                                    screenshot_raw
                                    if isinstance(screenshot_raw, dict)
                                    else {"consolidated_analysis": screenshot_raw or ""}
                                )
                                screenshot_data = parse_screenshot_result(raw_dict)
                                before_count = len(result.get("speakers", []))
                                merged_result = merge_with_screenshot_data(result, screenshot_data)
                                after_count = len(merged_result.get("speakers", []))
                                result = merged_result
                                screenshot_summary = {
                                    "speakers_before": before_count,
                                    "speakers_after": after_count,
                                    "screenshot_speakers": len(screenshot_data.get("speakers", [])),
                                    "speakers_added": max(after_count - before_count, 0),
                                }
                                used_screenshot = True
                                fallback_triggered = True
                                auto_screenshot_triggered = auto_screenshot_needed
                            except Exception as screenshot_exc:  # noqa: BLE001
                                st.warning(f"Screenshot fallback failed: {screenshot_exc}", icon="⚠️")

                st.session_state.scrape_runs.append(
                    ScrapeRun(
                        url=url,
                        prompt=prompt,
                        success=True,
                        used_ocr=current_use_ocr,
                        fallback_triggered=fallback_triggered,
                        used_omni=used_omni,
                        used_screenshot=used_screenshot,
                        auto_screenshot_triggered=auto_screenshot_triggered,
                        ocr_transcripts=transcripts,
                        screenshot_summary=screenshot_summary,
                        data=result,
                    )
                )
            except Exception as exc:  # pylint: disable=broad-except
                st.session_state.scrape_runs.append(
                    ScrapeRun(
                        url=url,
                        prompt=prompt,
                        success=False,
                        error=str(exc),
                    )
                )


def render_results() -> None:
    """Display the aggregated scrape results."""
    if not st.session_state.get("scrape_runs"):
        st.info("Results will appear here after you run the scraper.")
        return

    successes = [run for run in st.session_state.scrape_runs if run.success]
    failures = [run for run in st.session_state.scrape_runs if not run.success]

    if successes:
        st.subheader("Scrape Results")
        for run in successes:
            event = run.data.get("event", {})
            speakers = run.data.get("speakers", [])
            badges = []
            if run.used_ocr:
                badges.append("OCR")
            if run.used_omni:
                badges.append("omni")
            if run.used_screenshot:
                badges.append("screenshot auto" if run.auto_screenshot_triggered else "screenshot")
            elif run.fallback_triggered:
                badges.append("auto retry")
            badge_text = f" ({', '.join(badges)})" if badges else ""

            st.markdown(f"**URL:** {run.url}{badge_text}")

            with st.expander("Event details", expanded=False):
                st.write(event)

            if speakers:
                st.dataframe(speakers, use_container_width=True)
            else:
                st.warning("No speakers found on this page.")

            if run.used_screenshot and run.screenshot_summary:
                added = run.screenshot_summary.get("speakers_added", 0)
                if added:
                    st.caption(f"Screenshot fallback added {added} more speakers.")
                else:
                    st.caption("Screenshot fallback refined existing speaker details.")
                if run.auto_screenshot_triggered:
                    st.caption("Screenshot fallback ran automatically because the initial scrape looked incomplete. Please review for hallucinations.")
            elif run.used_screenshot and run.auto_screenshot_triggered:
                st.caption("Screenshot fallback ran automatically because the initial scrape looked incomplete. Please review for hallucinations.")
            if run.fallback_triggered and not run.used_screenshot:
                st.caption("Fallback enabled because most speakers lacked structured details.")
            if run.ocr_transcripts:
                with st.expander("OCR transcripts", expanded=False):
                    st.write(run.ocr_transcripts)

        aggregated = {
            "results": [asdict(run) for run in st.session_state.scrape_runs],
        }
        st.download_button(
            label="Download aggregated JSON",
            data=json.dumps(aggregated, indent=2, ensure_ascii=False),
            file_name="speaker_scrapes.json",
            mime="application/json",
        )

    if failures:
        st.subheader("Errors")
        for run in failures:
            st.error(f"{run.url}: {run.error}")


def main() -> None:
    """Entry point for the Streamlit app."""
    st.set_page_config(page_title="Speaker Scraper", page_icon="🕸️", layout="wide")
    ensure_session_state()

    st.title("Speaker Scraper Dashboard")
    st.caption(
        "Batch-run SmartScraperGraph to collect speaker details from multiple event pages."
    )

    api_key_present = bool(os.getenv("OPENAI_API_KEY"))
    if not api_key_present:
        st.warning(
            "OPENAI_API_KEY not found. Set it in the environment or the project `.env` file before running."
        )

    with st.sidebar:
        st.header("Configuration")
        model = st.selectbox(
            "Chat model",
            options=[
                "openai/gpt-4o-mini",
                "openai/gpt-4o",
                "openai/gpt-4.1-mini",
            ],
            index=0,
        )
        headless = st.toggle("Run browser headless", value=True)
        render_js = st.toggle(
            "Render JavaScript (network idle)",
            value=False,
            help="Enable Playwright's network idle wait for pages that need JS rendering.",
        )
        scroll_to_bottom = st.toggle(
            "Scroll page to bottom",
            value=False,
            help="Useful for sliders or lazy-loaded speaker lists.",
        )
        if scroll_to_bottom:
            scroll_sleep = st.slider(
                "Scroll delay (seconds)",
                min_value=0.5,
                max_value=5.0,
                value=1.5,
                step=0.5,
            )
            scroll_timeout = st.slider(
                "Scroll timeout (seconds)",
                min_value=30,
                max_value=240,
                value=120,
                step=10,
            )
        else:
            scroll_sleep = 1.5
            scroll_timeout = 120

        retry_limit = st.number_input(
            "Fetch retry limit",
            min_value=1,
            max_value=5,
            value=1,
            help="Number of times the Chromium loader retries on failure.",
        )

        use_ocr = st.toggle(
            "Enable OCR (image-to-text)",
            value=False,
            help=(
                "Switch to OmniScraperGraph and use OpenAI vision to read speaker details embedded in images. "
                "Requires a vision-capable model such as gpt-4o."
            ),
        )
        if use_ocr:
            max_images = st.slider(
                "Max images to analyse per page",
                min_value=1,
                max_value=20,
                value=6,
            )
            st.caption(
                "Tip: install `pip install scrapegraphai[ocr]` if you also want Surya OCR as a fallback."
            )
            if not is_vision_model(model):
                st.warning(
                    "The selected chat model does not support image inputs. OCR will be skipped until you switch to a vision-capable model such as gpt-4o.",
                    icon="⚠️",
                )
        else:
            max_images = 6
        omni_fallback = st.toggle(
            "Retry with OmniScraperGraph when data missing",
            value=False,
            help="If SmartScraperGraph leaves many fields empty, rerun the page with OmniScraperGraph (requires vision model).",
        )
        screenshot_fallback = st.toggle(
            "Fallback to ScreenshotScraperGraph",
            value=False,
            help="Capture full-page screenshots and extract text when speakers are embedded in images (requires vision model).",
        )
        st.caption("Screenshot fallback will auto-run when the HTML scrape looks incomplete; enable this toggle to force it on every page.")

    effective_use_ocr = use_ocr and is_vision_model(model)
    if use_ocr and not effective_use_ocr:
        st.caption("OCR disabled for this run because the selected model lacks vision support.")

    effective_omni = omni_fallback and is_vision_model(model)
    if omni_fallback and not effective_omni:
        st.caption("Omni fallback disabled because the selected model lacks vision support.")

    effective_screenshot = screenshot_fallback and is_vision_model(model)
    if screenshot_fallback and not effective_screenshot:
        st.caption("Screenshot fallback disabled because the selected model lacks vision support.")

    st.markdown("---")
    st.markdown("Need help? See the README for installation instructions.")

    prompt = st.text_area(
        "Extraction prompt",
        value=DEFAULT_PROMPT,
        height=260,
        help="Customize the instructions that will be sent to the LLM.",
    )
    raw_urls = st.text_area(
        "Event websites (one per line)",
        height=200,
        placeholder="https://example.com/speakers\nhttps://another.com/lineup",
    )

    urls = [line.strip() for line in raw_urls.splitlines() if line.strip()]

    run_button = st.button(
        "Run Scraper", type="primary", disabled=not (urls and api_key_present)
    )

    loader_kwargs: dict = {}
    if render_js:
        loader_kwargs["requires_js_support"] = True
    if scroll_to_bottom:
        loader_kwargs["backend"] = "playwright_scroll"
        loader_kwargs["scroll_to_bottom"] = True
        loader_kwargs["sleep"] = scroll_sleep
        loader_kwargs["timeout"] = scroll_timeout
    if retry_limit != 1:
        loader_kwargs["retry_limit"] = retry_limit

    if run_button:
        run_scraper(
            urls=urls,
            prompt=prompt,
            model=model,
            headless=headless,
            loader_kwargs=loader_kwargs,
            use_ocr=effective_use_ocr,
            max_images=max_images,
            omni_fallback=effective_omni,
            screenshot_fallback=effective_screenshot,
        )

    render_results()


if __name__ == "__main__":
    main()
