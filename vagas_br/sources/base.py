"""Shared helpers for job sources: HTTP client, retries, slugs, dates."""

from __future__ import annotations

import html
import logging
import re
import time
import unicodedata
from collections.abc import Callable, Iterable
from datetime import datetime, timedelta
from typing import Protocol

import httpx

from ..models import Job

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0 Safari/537.36"
)
DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
}

log = logging.getLogger("vagas_br")


class Source(Protocol):
    """A job source: yields :class:`Job` objects for the given queries."""

    name: str

    def collect(
        self, queries: list[str], max_pages: int, http: httpx.Client
    ) -> Iterable[Job]: ...


def make_client(timeout: float = 30.0) -> httpx.Client:
    """Build the shared HTTP client."""
    return httpx.Client(
        headers=DEFAULT_HEADERS, timeout=timeout, follow_redirects=True, http2=False
    )


def get(
    http: httpx.Client,
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    retries: int = 3,
    pause: float = 0.8,
) -> httpx.Response | None:
    """GET with simple retry/backoff. Returns ``None`` after repeated failure."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            r = http.get(url, params=params, headers=headers)
            if r.status_code == 429 or r.status_code >= 500:
                raise httpx.HTTPStatusError(
                    f"status {r.status_code}", request=r.request, response=r
                )
            if r.status_code >= 400:
                log.warning("GET %s -> %s", r.url, r.status_code)
                return None
            time.sleep(pause)
            return r
        except (httpx.HTTPError, httpx.HTTPStatusError) as exc:  # pragma: no cover
            last_error = exc
            wait = pause * (2**attempt)
            log.warning("GET %s failed (%s), retry in %.1fs", url, exc, wait)
            time.sleep(wait)
    log.error("GET %s gave up: %s", url, last_error)
    return None


def slugify(text: str) -> str:
    """``Engenheiro de Software`` -> ``engenheiro-de-software``."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")


def clean(text: str | None) -> str | None:
    """Collapse whitespace; return ``None`` for empty strings."""
    if text is None:
        return None
    t = " ".join(html.unescape(text).split())
    return t or None


_REL_RE = re.compile(
    r"(?:h[aá]\s+)?(\d+)\s*(minuto|hora|dia|semana|m[eê]s|mes|ano|minute|hour|day|week|month|year)s?",
    re.I,
)


def parse_date(text: str | None) -> str | None:
    """Normalise ``2026-09-10T21:17:01Z``, ``10/08/2026``, ``há 3 dias``, ``Hoje``.

    Returns an ISO date (``YYYY-MM-DD``) or ``None``.
    """
    if not text:
        return None
    t = text.strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", t)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.match(r"(\d{2})/(\d{2})/(\d{4})", t)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    today = datetime.now().date()  # board dates are Brazil-local, not UTC
    low = t.lower()
    if low in {"hoje", "today", "nova", "agora", "now"}:
        return today.isoformat()
    if low in {"ontem", "yesterday"}:
        return (today - timedelta(days=1)).isoformat()
    m = _REL_RE.search(low)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        if unit.startswith(("minuto", "hora", "minute", "hour")):
            delta = timedelta(days=0)
        elif unit.startswith(("dia", "day")):
            delta = timedelta(days=n)
        elif unit.startswith(("semana", "week")):
            delta = timedelta(weeks=n)
        elif unit.startswith(("m", "mes", "mês", "month")):
            delta = timedelta(days=30 * n)
        else:
            delta = timedelta(days=365 * n)
        return (today - delta).isoformat()
    return None


def dedupe(jobs: Iterable[Job], key: Callable[[Job], str] | None = None) -> list[Job]:
    """Drop duplicates by ``(source, external_id)`` (or a custom key)."""
    seen: set[str] = set()
    out: list[Job] = []
    for j in jobs:
        k = key(j) if key else f"{j.source}:{j.external_id}"
        if k in seen:
            continue
        seen.add(k)
        out.append(j)
    return out
