"""Generic LLM-powered source using ScrapeGraphAI's ``SmartScraperGraph``.

Used for JavaScript-rendered boards (Remotar, Coodesh, ...) that have no
public API. Each target is a listing URL plus a prompt; the graph renders the
page with Playwright, feeds it to the configured LLM and returns a structured
list of jobs following :class:`JobList`.

Requires an LLM API key. Configure through environment variables::

    VAGAS_LLM_MODEL   e.g. "google_genai/gemini-2.5-flash" (default),
                      "openai/gpt-4o-mini", "ollama/llama3.1"
    GEMINI_API_KEY / GOOGLE_API_KEY / OPENAI_API_KEY   as appropriate
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field

from ..models import Job
from .base import clean, log, parse_date

NAME = "sgai"
DEFAULT_MODEL = "google_genai/gemini-2.5-flash"

PROMPT = (
    "Esta página lista vagas de emprego de tecnologia no Brasil. Extraia TODAS as "
    "vagas visíveis. Para cada vaga informe: title (cargo), company (empresa), "
    "url (link absoluto ou relativo para a vaga), location (cidade/estado ou "
    "'Remoto'), contract (CLT, PJ, Estágio, Freelance ou vazio se não indicado), "
    "workplace (remoto, hibrido ou presencial se indicado), seniority (junior, "
    "pleno, senior, estagio se indicado), tags (tecnologias citadas), "
    "published (data ou texto como 'há 3 dias'), salary (se houver). "
    "Não invente dados: deixe vazio o que não aparecer."
)


class JobItem(BaseModel):
    title: str
    company: str | None = None
    url: str | None = None
    location: str | None = None
    contract: str | None = None
    workplace: str | None = None
    seniority: str | None = None
    tags: list[str] = Field(default_factory=list)
    published: str | None = None
    salary: str | None = None


class JobList(BaseModel):
    jobs: list[JobItem] = Field(default_factory=list)


@dataclass(frozen=True)
class Target:
    """A listing page to scrape with the LLM graph."""

    name: str
    url: str
    prompt: str = PROMPT


DEFAULT_TARGETS: tuple[Target, ...] = (
    Target("remotar", "https://remotar.com.br/"),
    Target("coodesh", "https://coodesh.com/vagas"),
    Target("apinfo", "https://www.apinfo.com/apinfo/inc/list4.cfm"),
)

_CONTRACT_MAP = {
    "clt": "CLT",
    "pj": "PJ",
    "clt/pj": "CLT/PJ",
    "clt ou pj": "CLT/PJ",
    "estágio": "ESTAGIO",
    "estagio": "ESTAGIO",
    "freelance": "FREELANCE",
    "freelancer": "FREELANCE",
    "temporário": "TEMPORARIO",
}


def llm_config() -> dict | None:
    """Build the ScrapeGraphAI ``llm`` config from the environment."""
    model = os.getenv("VAGAS_LLM_MODEL", DEFAULT_MODEL)
    provider = model.split("/", 1)[0]
    key = None
    if provider == "google_genai":
        key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    elif provider == "openai":
        key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_APIKEY")
    elif provider == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
    elif provider == "groq":
        key = os.getenv("GROQ_API_KEY")
    elif provider == "mistralai":
        key = os.getenv("MISTRAL_API_KEY")
    elif provider == "ollama":
        key = "ollama"
    if not key:
        return None
    cfg: dict = {"model": model, "temperature": 0}
    if provider != "ollama":
        cfg["api_key"] = key
    else:
        cfg["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return cfg


class ScrapeGraphSource:
    """Scrape arbitrary listing pages with ``SmartScraperGraph``."""

    name = NAME

    def __init__(self, targets: Iterable[Target] = DEFAULT_TARGETS) -> None:
        self.targets = list(targets)

    def collect(
        self, queries: list[str], max_pages: int, http: httpx.Client
    ) -> Iterable[Job]:
        cfg = llm_config()
        if cfg is None:
            log.warning(
                "sgai: no LLM API key found (GEMINI_API_KEY / OPENAI_API_KEY ...); "
                "skipping LLM sources"
            )
            return
        from scrapegraphai.graphs import SmartScraperGraph

        graph_config = {"llm": cfg, "verbose": False, "headless": True}
        for target in self.targets:
            log.info("sgai: scraping %s (%s)", target.name, target.url)
            try:
                graph = SmartScraperGraph(
                    prompt=target.prompt,
                    source=target.url,
                    config=graph_config,
                    schema=JobList,
                )
                result = graph.run()
            except Exception as exc:  # noqa: BLE001 - external service
                log.error("sgai: %s failed: %s", target.name, exc)
                continue
            for item in _items(result):
                job = self._to_job(target, item)
                if job:
                    yield job

    @staticmethod
    def _to_job(target: Target, item: dict) -> Job | None:
        title = clean(item.get("title"))
        if not title:
            return None
        url = clean(item.get("url")) or target.url
        url = urljoin(target.url, url)
        contract = _CONTRACT_MAP.get((item.get("contract") or "").strip().lower())
        workplace = (item.get("workplace") or "").strip().lower() or None
        if workplace not in {"remoto", "hibrido", "presencial"}:
            workplace = None
        seniority = (item.get("seniority") or "").strip().lower() or None
        if seniority not in {"estagio", "junior", "pleno", "senior", "especialista"}:
            seniority = None
        return Job(
            source=f"{NAME}:{target.name}",
            external_id=url,
            title=title,
            url=url,
            company=clean(item.get("company")),
            location_raw=clean(item.get("location")),
            contract=contract,
            workplace=workplace,
            seniority=seniority,
            tags=[t for t in (clean(x) for x in item.get("tags") or []) if t],
            published_at=parse_date(item.get("published")),
            salary=clean(item.get("salary")),
        )


def _items(result) -> list[dict]:
    """Unwrap whatever shape the graph returned into a list of dicts."""
    if result is None:
        return []
    if isinstance(result, BaseModel):
        result = result.model_dump()
    if isinstance(result, dict):
        if "jobs" in result and isinstance(result["jobs"], list):
            return [i for i in result["jobs"] if isinstance(i, dict)]
        if "content" in result:
            return _items(result["content"])
        return [result] if "title" in result else []
    if isinstance(result, list):
        return [i for i in result if isinstance(i, dict)]
    return []
