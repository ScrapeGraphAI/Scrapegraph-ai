"""Programathor (programathor.com.br) - Brazilian dev-only job board."""

from __future__ import annotations

import re
from collections.abc import Iterable

import httpx
from bs4 import BeautifulSoup

from ..models import Job
from .base import clean, get, parse_date

NAME = "programathor"
BASE = "https://programathor.com.br"
_ID_RE = re.compile(r"/jobs/(\d+)")
_CONTRACT_MAP = {
    "pj": "PJ",
    "clt": "CLT",
    "estágio": "ESTAGIO",
    "estagio": "ESTAGIO",
    "freelance": "FREELANCE",
    "temporário": "TEMPORARIO",
}
_SENIORITY_MAP = {
    "júnior": "junior",
    "junior": "junior",
    "pleno": "pleno",
    "sênior": "senior",
    "senior": "senior",
    "estágio": "estagio",
    "especialista": "especialista",
}


class ProgramathorSource:
    name = NAME

    def collect(
        self, queries: list[str], max_pages: int, http: httpx.Client
    ) -> Iterable[Job]:
        # The board only lists tech jobs, so queries are not needed: walk pages.
        for page in range(1, max_pages + 1):
            r = get(http, f"{BASE}/jobs", params={"page": page})
            if r is None:
                break
            soup = BeautifulSoup(r.text, "html.parser")
            cells = soup.select(".cell-list")
            if not cells:
                break
            for cell in cells:
                job = self._parse(cell)
                if job:
                    yield job

    @staticmethod
    def _parse(cell) -> Job | None:
        a = cell.select_one("a[href^='/jobs/']")
        if not a:
            return None
        href = a["href"]
        m = _ID_RE.search(href)
        ext = m.group(1) if m else href
        title = (
            clean(cell.select_one("h3").get_text(" "))
            if cell.select_one("h3")
            else None
        )
        if not title:
            return None
        spans = [
            clean(s.get_text(" ")) for s in cell.select(".cell-list-content-icon span")
        ]
        spans = [s for s in spans if s]
        company = spans[0] if spans else None
        location = spans[1] if len(spans) > 1 else None
        contract = None
        seniority = None
        for s in spans[2:]:
            low = s.lower()
            if low in _CONTRACT_MAP:
                contract = _CONTRACT_MAP[low]
            elif low in _SENIORITY_MAP:
                seniority = _SENIORITY_MAP[low]
        tags = [clean(t.get_text()) for t in cell.select(".tag-list")]
        published = None
        date_el = cell.select_one(".cell-list-content-icon + div, .text-muted, .date")
        if date_el:
            published = parse_date(clean(date_el.get_text(" ")))
        return Job(
            source=NAME,
            external_id=ext,
            title=title,
            url=f"{BASE}{href}",
            company=company,
            location_raw=location,
            contract=contract,
            seniority=seniority,
            tags=[t for t in tags if t],
            published_at=published,
        )
