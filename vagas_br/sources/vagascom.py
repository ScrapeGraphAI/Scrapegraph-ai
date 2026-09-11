"""Vagas.com (vagas.com.br) search result pages."""

from __future__ import annotations

from collections.abc import Iterable

import httpx
from bs4 import BeautifulSoup

from ..models import Job
from .base import clean, get, parse_date, slugify

NAME = "vagascom"
BASE = "https://www.vagas.com.br"
_LEVEL_MAP = {
    "júnior/trainee": "junior",
    "junior/trainee": "junior",
    "pleno": "pleno",
    "sênior": "senior",
    "senior": "senior",
    "estágio": "estagio",
    "estagio": "estagio",
    "supervisão/coordenação": "lideranca",
    "gerência": "lideranca",
    "especialista": "especialista",
}


class VagasComSource:
    name = NAME

    def collect(
        self, queries: list[str], max_pages: int, http: httpx.Client
    ) -> Iterable[Job]:
        for q in queries:
            for page in range(1, max_pages + 1):
                params = {"ordenar_por": "mais_recentes"}
                if page > 1:
                    params["pagina"] = page
                r = get(http, f"{BASE}/vagas-de-{slugify(q)}", params=params)
                if r is None:
                    break
                soup = BeautifulSoup(r.text, "html.parser")
                cards = soup.select("li.vaga")
                if not cards:
                    break
                for li in cards:
                    job = self._parse(li, q)
                    if job:
                        yield job

    @staticmethod
    def _parse(li, query: str) -> Job | None:
        a = li.select_one("a.link-detalhes-vaga")
        if not a:
            return None
        ext = a.get("data-id-vaga") or a.get("href")
        title = clean(a.get("title") or a.get_text(" "))
        if not title:
            return None
        company = (
            clean(li.select_one(".emprVaga").get_text(" "))
            if li.select_one(".emprVaga")
            else None
        )
        level_el = li.select_one(".nivelVaga")
        level = clean(level_el.get_text(" ")) if level_el else None
        loc_el = li.select_one(".vaga-local")
        location = None
        if loc_el:
            for tip in loc_el.select(".tooltip-place"):
                tip.decompose()
            location = clean(loc_el.get_text(" "))
        date_el = li.select_one(".data-publicacao")
        published = parse_date(clean(date_el.get_text(" "))) if date_el else None
        desc_el = li.select_one(".detalhes")
        desc = clean(desc_el.get_text(" ")) if desc_el else None
        return Job(
            source=NAME,
            external_id=str(ext),
            title=title,
            url=f"{BASE}{a['href']}",
            company=company,
            location_raw=location,
            seniority=_LEVEL_MAP.get((level or "").lower()),
            published_at=published,
            description=desc,
            query=query,
        )
