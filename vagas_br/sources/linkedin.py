"""LinkedIn guest job search (public HTML fragments, no login)."""

from __future__ import annotations

import re
from collections.abc import Iterable

import httpx
from bs4 import BeautifulSoup

from ..models import Job
from .base import clean, get, log, parse_date

NAME = "linkedin"
API = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
BRAZIL_GEO_ID = "106057199"
_ID_RE = re.compile(r"(\d{6,})")


class LinkedInSource:
    name = NAME

    def collect(
        self, queries: list[str], max_pages: int, http: httpx.Client
    ) -> Iterable[Job]:
        for q in queries:
            start = 0
            # LinkedIn returns ~10 cards per call; treat a "page" as 25 results.
            limit = max_pages * 25
            while start < limit:
                r = get(
                    http,
                    API,
                    params={
                        "keywords": q,
                        "location": "Brasil",
                        "geoId": BRAZIL_GEO_ID,
                        "f_TPR": "r2592000",  # last 30 days
                        "sortBy": "DD",
                        "start": start,
                    },
                )
                if r is None or not r.text.strip():
                    break
                soup = BeautifulSoup(r.text, "html.parser")
                cards = soup.select("li")
                if not cards:
                    break
                got = 0
                for li in cards:
                    job = self._parse_card(li, q)
                    if job:
                        got += 1
                        yield job
                if got == 0:
                    break
                start += len(cards)
        log.debug("linkedin done")

    @staticmethod
    def _parse_card(li, query: str) -> Job | None:
        link = li.select_one("a.base-card__full-link") or li.select_one("a[href]")
        if not link:
            return None
        href = link.get("href", "").split("?")[0]
        urn = li.select_one("[data-entity-urn]")
        ext = None
        if urn:
            m = _ID_RE.search(urn.get("data-entity-urn", ""))
            ext = m.group(1) if m else None
        if not ext:
            m = _ID_RE.search(href)
            ext = m.group(1) if m else href
        title = clean((li.select_one(".base-search-card__title") or link).get_text(" "))
        company = clean(
            (
                li.select_one(".base-search-card__subtitle") or li.select_one("h4")
            ).get_text(" ")
            if (li.select_one(".base-search-card__subtitle") or li.select_one("h4"))
            else None
        )
        loc = clean(
            li.select_one(".job-search-card__location").get_text(" ")
            if li.select_one(".job-search-card__location")
            else None
        )
        t = li.select_one("time")
        published = parse_date(t.get("datetime")) if t else None
        if not title:
            return None
        return Job(
            source=NAME,
            external_id=ext,
            title=title,
            url=href,
            company=company,
            location_raw=loc,
            published_at=published,
            query=query,
        )
