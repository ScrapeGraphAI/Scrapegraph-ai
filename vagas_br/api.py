"""FastAPI app: JSON API + static page.

Run with::

    uvicorn vagas_br.api:app --reload --port 8000
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import storage
from .geo import REGIONS, UFS
from .models import AREAS, CONTRACTS, SENIORITIES, WORKPLACES

STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Vagas Tech Brasil", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")

ListParam = Annotated[list[str] | None, Query()]


def _filters(
    q: str | None,
    uf: list[str] | None,
    regiao: list[str] | None,
    contrato: list[str] | None,
    modelo: list[str] | None,
    senioridade: list[str] | None,
    area: list[str] | None,
    fonte: list[str] | None,
    tag: list[str] | None,
    cidade: str | None,
    dias: int | None,
) -> dict:
    return {
        "q": q,
        "uf": [u.upper() for u in uf] if uf else None,
        "region": regiao,
        "contract": contrato,
        "workplace": modelo,
        "seniority": senioridade,
        "area": area,
        "source": fonte,
        "tag": tag,
        "city": cidade,
        "days": dias,
    }


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")


@app.get("/api/jobs")
def list_jobs(
    q: str | None = None,
    uf: ListParam = None,
    regiao: ListParam = None,
    contrato: ListParam = None,
    modelo: ListParam = None,
    senioridade: ListParam = None,
    area: ListParam = None,
    fonte: ListParam = None,
    tag: ListParam = None,
    cidade: str | None = None,
    dias: int | None = None,
    page: int = 1,
    per_page: int = 50,
    order: str = "recent",
) -> JSONResponse:
    f = _filters(
        q, uf, regiao, contrato, modelo, senioridade, area, fonte, tag, cidade, dias
    )
    conn = storage.connect()
    try:
        data = storage.query_jobs(conn, f, page=page, per_page=per_page, order=order)
    finally:
        conn.close()
    return JSONResponse(data)


@app.get("/api/facets")
def list_facets(
    q: str | None = None,
    uf: ListParam = None,
    regiao: ListParam = None,
    contrato: ListParam = None,
    modelo: ListParam = None,
    senioridade: ListParam = None,
    area: ListParam = None,
    fonte: ListParam = None,
    tag: ListParam = None,
    cidade: str | None = None,
    dias: int | None = None,
) -> JSONResponse:
    f = _filters(
        q, uf, regiao, contrato, modelo, senioridade, area, fonte, tag, cidade, dias
    )
    conn = storage.connect()
    try:
        data = storage.facets(conn, f)
    finally:
        conn.close()
    return JSONResponse(data)


@app.get("/api/meta")
def meta() -> JSONResponse:
    conn = storage.connect()
    try:
        s = storage.stats(conn)
    finally:
        conn.close()
    return JSONResponse(
        {
            "ufs": [
                {"uf": uf, "name": name, "region": region}
                for uf, (name, region) in UFS.items()
            ],
            "regions": REGIONS,
            "contracts": CONTRACTS,
            "workplaces": WORKPLACES,
            "seniorities": SENIORITIES,
            "areas": AREAS,
            **s,
        }
    )
