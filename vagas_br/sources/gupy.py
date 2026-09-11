"""Gupy public job portal (JSON API). Biggest ATS in Brazil."""

from __future__ import annotations

from collections.abc import Iterable

import httpx

from ..geo import uf_from_state_name
from ..models import Job
from .base import clean, get, log, parse_date

NAME = "gupy"
API = "https://employability-portal.gupy.io/api/v1/jobs"
PAGE = 100

_TYPE_MAP = {
    "vacancy_type_effective": "CLT",
    "vacancy_legal_entity": "PJ",
    "vacancy_type_legal_entity": "PJ",
    "vacancy_type_internship": "ESTAGIO",
    "vacancy_type_apprentice": "APRENDIZ",
    "vacancy_type_temporary": "TEMPORARIO",
    "vacancy_type_outsource": "TERCEIRIZADO",
    "vacancy_type_freelancer": "FREELANCE",
    "vacancy_type_autonomous": "FREELANCE",
    "vacancy_type_associate": "OUTRO",
    "vacancy_type_talent_pool": "OUTRO",
    "vacancy_type_lecturer": "OUTRO",
    "vacancy_type_volunteer": "OUTRO",
}
_WORKPLACE_MAP = {"remote": "remoto", "hybrid": "hibrido", "on-site": "presencial"}


def _to_job(item: dict, query: str) -> Job | None:
    url = item.get("jobUrl")
    if not url or (item.get("country") or "Brasil") not in {"Brasil", "Brazil", "BR"}:
        return None
    city = clean(item.get("city"))
    state = clean(item.get("state"))
    uf = uf_from_state_name(state)
    workplace = _WORKPLACE_MAP.get(item.get("workplaceType") or "")
    if item.get("isRemoteWork"):
        workplace = "remoto"
    loc = ", ".join(p for p in (city, state) if p) or None
    return Job(
        source=NAME,
        external_id=str(item["id"]),
        title=clean(item.get("name")) or "(sem título)",
        url=url,
        company=clean(item.get("careerPageName")),
        location_raw=loc,
        city=city,
        uf=uf,
        workplace=workplace,
        contract=_TYPE_MAP.get(item.get("type") or ""),
        published_at=parse_date(item.get("publishedDate")),
        description=(
            clean(item.get("description"))[:4000] if item.get("description") else None
        ),
        tags=[clean(s) for s in (item.get("skills") or []) if clean(s)][:20],
        query=query,
    )


class GupySource:
    name = NAME

    def collect(
        self, queries: list[str], max_pages: int, http: httpx.Client
    ) -> Iterable[Job]:
        for q in queries:
            offset = 0
            for _ in range(max_pages):
                r = get(
                    http,
                    API,
                    params={"jobName": q, "limit": PAGE, "offset": offset},
                    headers={"Accept": "application/json"},
                )
                if r is None:
                    break
                try:
                    payload = r.json()
                except ValueError:
                    log.warning("gupy: invalid JSON for %r offset %s", q, offset)
                    break
                items = payload.get("data") or []
                for item in items:
                    job = _to_job(item, q)
                    if job:
                        yield job
                total = (payload.get("pagination") or {}).get("total", 0)
                offset += PAGE
                if len(items) < PAGE or offset >= total:
                    break
