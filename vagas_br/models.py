"""Data model shared by every job source."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

CONTRACTS = [
    "CLT",
    "PJ",
    "CLT/PJ",
    "ESTAGIO",
    "TEMPORARIO",
    "FREELANCE",
    "TERCEIRIZADO",
    "APRENDIZ",
    "OUTRO",
]
WORKPLACES = ["remoto", "hibrido", "presencial"]
SENIORITIES = ["estagio", "junior", "pleno", "senior", "especialista", "lideranca"]
AREAS = [
    "backend",
    "frontend",
    "fullstack",
    "mobile",
    "dados",
    "devops",
    "qa",
    "seguranca",
    "infra",
    "suporte",
    "erp",
    "produto",
    "gestao",
    "outro",
]


@dataclass
class Job:
    """One job opening, normalised across sources.

    ``source`` + ``external_id`` uniquely identify a posting. Fields that a
    source cannot provide are left ``None`` and filled by
    :func:`vagas_br.normalize.enrich` from the free text.
    """

    source: str
    external_id: str
    title: str
    url: str
    company: str | None = None
    location_raw: str | None = None
    city: str | None = None
    uf: str | None = None
    region: str | None = None
    workplace: str | None = None
    contract: str | None = None
    seniority: str | None = None
    area: str | None = None
    tags: list[str] = field(default_factory=list)
    salary: str | None = None
    published_at: str | None = None
    description: str | None = None
    query: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return a plain ``dict`` (tags kept as a list)."""
        return asdict(self)

    @property
    def text(self) -> str:
        """All free text of the job, used for keyword detection."""
        return " \n ".join(
            p for p in (self.title, self.location_raw, self.description) if p
        )
