from typing import Annotated

from fastapi import APIRouter, Query, Response

from .. import schemas
from ..services import logging_service

router = APIRouter(prefix="/api", tags=["logs"])


@router.get("/logs", response_model=list[schemas.LogEntry])
def get_logs(
    level: Annotated[list[str] | None, Query(title="Filter by level")] = None,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    after: Annotated[str | None, Query(title="Only entries after this ISO timestamp")] = None,
) -> list[schemas.LogEntry]:
    levels: tuple[str, ...] | None = tuple(level) if level else None
    return logging_service.read_logs(levels=levels, limit=limit, after=after)


@router.delete("/logs")
def clear_logs() -> Response:
    logging_service.clear_logs()
    return Response(status_code=204)
