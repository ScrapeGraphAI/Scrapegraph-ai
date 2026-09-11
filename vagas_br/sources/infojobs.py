"""InfoJobs Brasil (infojobs.com.br) search result pages."""

from __future__ import annotations

import re
from collections.abc import Iterable

import httpx
from bs4 import BeautifulSoup

from ..geo import UFS, strip_accents
from ..models import Job
from .base import clean, get, parse_date, slugify

NAME = "infojobs"
BASE = "https://www.infojobs.com.br"
_ID_RE = re.compile(r"__(\d+)\.aspx")
_KM_RE = re.compile(r",?\s*\d+\s*km\s+de\s+voc[eê]\.?", re.I)


class InfoJobsSource:
    name = NAME

    def collect(
        self, queries: list[str], max_pages: int, http: httpx.Client
    ) -> Iterable[Job]:
        # InfoJobs paginates via JS; national page + one page per state gives
        # broad coverage without pagination.
        state_slugs = [""] + [slugify(name) for _, (name, _) in UFS.items()]
        for q in queries:
            for i, state in enumerate(state_slugs):
                if i >= max_pages:
                    break
                suffix = f"-em-{state}" if state else ""
                url = f"{BASE}/vagas-de-emprego-{slugify(q)}{suffix}.aspx"
                r = get(http, url)
                if r is None:
                    continue
                soup = BeautifulSoup(r.text, "html.parser")
                for card in soup.select("[data-href]"):
                    job = self._parse(card, q)
                    if job:
                        yield job

    @staticmethod
    def _parse(card, query: str) -> Job | None:
        href = card.get("data-href")
        if not href:
            return None
        m = _ID_RE.search(href)
        ext = m.group(1) if m else href
        title_el = card.select_one(".js_vacancyTitle, h2, h3")
        title = clean(title_el.get_text(" ")) if title_el else None
        if not title:
            return None
        bodies = [clean(x.get_text(" ")) for x in card.select(".text-body")]
        bodies = [b for b in bodies if b and b != title]
        company = bodies[0] if bodies else None
        # Location is the element right after the company, usually "Cidade - UF".
        location = None
        for el in card.select(".text-body, .text-medium, span, div"):
            txt = clean(el.get_text(" "))
            if txt and re.search(r"\s-\s(" + "|".join(UFS) + r")\b", txt):
                location = _KM_RE.sub("", txt).strip(" ,")
                break
        if not location:
            for el in card.select("div, span"):
                txt = clean(el.get_text(" "))
                if txt and strip_accents(txt) in {"home office", "remoto"}:
                    location = txt
                    break
        date_el = card.select_one(".js_date, .text-medium.small")
        published = parse_date(clean(date_el.get_text(" "))) if date_el else None
        meta = " | ".join(
            clean(x.get_text(" ")) or "" for x in card.select(".text-medium")
        )
        desc_el = card.select_one("p, .text-medium:last-of-type")
        desc = clean(desc_el.get_text(" ")) if desc_el else None
        return Job(
            source=NAME,
            external_id=ext,
            title=title,
            url=f"{BASE}{href}" if href.startswith("/") else href,
            company=company,
            location_raw=location,
            published_at=published,
            description=f"{meta}\n{desc or ''}".strip() or None,
            query=query,
        )
