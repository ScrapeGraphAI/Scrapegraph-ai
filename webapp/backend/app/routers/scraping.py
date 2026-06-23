import uuid

from fastapi import APIRouter

from .. import schemas
from ..services import logging_service, scraper

LOG = "api"
router = APIRouter(prefix="/api", tags=["scraping"])


@router.post("/scrape", response_model=schemas.ScrapeResponse)
def scrape(req: schemas.ScrapeRequest) -> schemas.ScrapeResponse:
    request_id = uuid.uuid4().hex[:8]
    logging_service.info(LOG, f"[{request_id}] POST /api/scrape source={req.source} llm={req.llm.provider}/{req.llm.model}")
    result = scraper.run_scrape(req)
    logging_service.info(LOG, f"[{request_id}] → {result.status}")
    return result
