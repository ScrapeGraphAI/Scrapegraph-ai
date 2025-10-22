"""
FastAPI Backend for Adaptive Speaker Scraper

Provides REST API for the frontend UI to scrape speaker data using
intelligent adaptive strategy (SmartScraperGraph, OmniScraperGraph, or ScreenshotScraperGraph).
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parents[3]
load_dotenv(dotenv_path=ROOT_DIR / ".env")

# Import our enhanced adaptive scraper
import sys
sys.path.insert(0, str(ROOT_DIR / "examples"))
from enhanced_adaptive_scraper import scrape_with_enhanced_strategy, SpeakerScrapeResult

app = FastAPI(title="Adaptive Speaker Scraper API")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage
JOBS: Dict[str, Dict] = {}

# Output directory
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


class ScrapeRequest(BaseModel):
    """Request model for scraping."""
    urls: List[str]
    timeout: Optional[int] = 60


def save_to_excel(data: dict, output_path: Path) -> None:
    """Save speaker data to Excel file."""
    import pandas as pd

    speakers = data.get("data", {}).get("speakers", [])
    event = data.get("data", {}).get("event", {})

    # Create DataFrame
    df = pd.DataFrame(speakers)

    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Speakers', index=False)

        # Add event metadata sheet
        event_df = pd.DataFrame([event])
        event_df.to_excel(writer, sheet_name='Event Info', index=False)

        # Add scraping metadata
        metadata = {
            "URL": data.get("url"),
            "Strategy Used": data.get("strategy_used"),
            "Website Type": data.get("website_type"),
            "Completeness Score": data.get("analysis", {}).get("completeness_score", 0),
            "Speakers Found": len(speakers),
            "Scraped At": datetime.now().isoformat()
        }
        metadata_df = pd.DataFrame([metadata])
        metadata_df.to_excel(writer, sheet_name='Metadata', index=False)


def get_website_name(url: str) -> str:
    """Extract clean website name from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        domain_parts = domain.split('.')
        if len(domain_parts) > 1:
            return domain_parts[0]
        return domain
    except Exception:
        return "unknown"


def run_scrape_job(job_id: str, urls: List[str], timeout: int):
    """Background task to run adaptive scraping."""
    try:
        JOBS[job_id]["status"] = "running"

        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY not found in environment")

        # Configuration for adaptive scraper
        config = {
            "llm": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": "openai/gpt-4o",  # Vision model for screenshots
                "temperature": 0,
                "max_tokens": 4000,  # Increased for better extraction from screenshots
            },
            "verbose": False,
            "headless": True,
            "loader_kwargs": {
                "scroll_to_bottom": False,  # Don't use height detection (unreliable with lazy loading)
                "scroll_timeout": 30,  # Scroll for 30 seconds total
                "sleep": 1,  # Wait 1 second between scrolls
                "scroll": 5000,  # Scroll 5000px at a time (minimum allowed)
            },
        }

        prompt = """
        You are analyzing a public event speaker page. Extract ALL speaker information that is VISIBLE AS TEXT on this page.

        This is publicly available speaker directory information for a business conference.

        IMPORTANT: Look for text labels, names, titles, and company names that appear on the page, including:
        1. Text overlays on speaker photos in the hero section
        2. Names and titles in speaker card sections
        3. Any speaker listings throughout the page

        For each speaker entry you find, extract the TEXT that appears showing:
          - full_name (as displayed)
          - first_name, last_name (parse from full_name)
          - company (organization name shown)
          - position (job title shown)
          - linkedin_url (if a LinkedIn link is visible)

        Also extract event metadata text:
          - event_name, event_dates, event_location, event_time

        Return ALL speaker entries found as structured JSON.

        Note: You are reading public text information from a speaker directory, not identifying faces.
        """

        # Process first URL (for now, single URL)
        url = urls[0]

        # Run enhanced adaptive scraper
        result = scrape_with_enhanced_strategy(
            url=url,
            prompt=prompt,
            config=config,
            schema=SpeakerScrapeResult,
            enable_linkedin_enrichment=False,  # Not implemented yet
        )

        speaker_count = len(result.get("data", {}).get("speakers", []))
        website_name = get_website_name(url)

        # Check if extraction failed
        if speaker_count == 0:
            JOBS[job_id] = {
                "status": "completed",
                "file_path": None,
                "error": f"Failed to extract speakers from {url}",
                "speaker_count": 0,
                "website_name": website_name,
                "url": url,
                "strategy_used": result.get("strategy_used"),
                "website_type": result.get("website_type"),
            }
            return

        # Save to Excel
        date_str = datetime.now().strftime('%Y_%m_%d')
        time_str = datetime.now().strftime('%H%M%S')
        filename = f"{website_name}_{date_str}_{time_str}.xlsx"
        output_path = OUTPUT_DIR / filename

        save_to_excel(result, output_path)

        # Update job status
        JOBS[job_id] = {
            "status": "completed",
            "file_path": str(output_path),
            "error": None,
            "speaker_count": speaker_count,
            "website_name": website_name,
            "url": url,
            "strategy_used": result.get("strategy_used"),
            "website_type": result.get("website_type"),
            "analysis": result.get("analysis", {}),
        }

    except Exception as e:
        JOBS[job_id] = {
            "status": "failed",
            "file_path": None,
            "error": str(e),
            "speaker_count": 0,
            "website_name": None,
        }


@app.post("/scrape_sga", status_code=202)
def start_scrape(req: ScrapeRequest, background_tasks: BackgroundTasks):
    """Start a new scraping job."""
    if not req.urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued", "file_path": None, "error": None}

    background_tasks.add_task(run_scrape_job, job_id, req.urls, req.timeout or 60)

    return {"job_id": job_id, "status": JOBS[job_id]["status"]}


@app.get("/status/{job_id}")
def get_status(job_id: str):
    """Get job status."""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **job}


@app.get("/download/{job_id}")
def download(job_id: str):
    """Download scraped file."""
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "completed" or not job.get("file_path"):
        raise HTTPException(status_code=409, detail="Job not completed")

    file_path = job["file_path"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=410, detail="File no longer available")

    return FileResponse(file_path, filename=os.path.basename(file_path))


# Serve static frontend
frontend_dir = Path(__file__).parent
app.mount("/ui", StaticFiles(directory=str(frontend_dir), html=True), name="ui")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
