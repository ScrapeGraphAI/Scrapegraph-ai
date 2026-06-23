from fastapi import APIRouter

from .. import schemas
from ..services import logging_service
from ..services.model_discovery import discover_ollama_models

LOG = "api"
router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models", response_model=schemas.ModelInfo)
def list_models() -> schemas.ModelInfo:
    logging_service.info(LOG, "GET /api/models")
    models = discover_ollama_models()
    logging_service.info(LOG, f"GET /api/models → {len(models)} available")
    return schemas.ModelInfo(ollama_models=models)
