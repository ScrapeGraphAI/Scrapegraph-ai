"""Unit tests for vagas_br location parsing and rule-based enrichment."""

import pytest

from vagas_br.geo import parse_location, region_of, uf_from_state_name
from vagas_br.models import Job
from vagas_br.normalize import (
    detect_contract,
    detect_seniority,
    enrich,
    is_tech_job,
)
from vagas_br.sources.base import parse_date


@pytest.mark.parametrize(
    "text, city, uf, workplace",
    [
        ("Belo Horizonte / MG", "Belo Horizonte", "MG", None),
        ("Curitiba - PR", "Curitiba", "PR", None),
        ("Campinas, São Paulo, Brazil", "Campinas", "SP", None),
        ("Paraná", None, "PR", None),
        ("Rio Grande do Sul", None, "RS", None),
        ("Remoto", None, None, "remoto"),
        ("100% Home Office", None, None, "remoto"),
        ("Brazil", None, None, None),
        ("Rio de Janeiro e Região", "Rio de Janeiro", "RJ", None),
        ("Brasília, Federal District, Brazil", "Brasília", "DF", None),
        ("Osasco (SP) híbrido", "Osasco", "SP", "hibrido"),
        ("Curitiba - PR , 0 Km de você.", "Curitiba", "PR", None),
        ("Blumenau", "Blumenau", "SC", None),
    ],
)
def test_parse_location(text, city, uf, workplace):
    loc = parse_location(text)
    assert loc["city"] == city
    assert loc["uf"] == uf
    assert loc["workplace"] == workplace


def test_state_helpers():
    assert uf_from_state_name("Minas Gerais") == "MG"
    assert uf_from_state_name("mg") == "MG"
    assert uf_from_state_name("Federal District") == "DF"
    assert region_of("SC") == "Sul"
    assert region_of(None) is None


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Contratação PJ", "PJ"),
        ("Regime CLT com benefícios", "CLT"),
        ("CLT ou PJ, a combinar", "CLT/PJ"),
        ("Vaga de estágio em TI", "ESTAGIO"),
        ("Nada de contrato aqui", None),
    ],
)
def test_detect_contract(text, expected):
    assert detect_contract(text) == expected


def test_detect_seniority_prefers_title():
    assert detect_seniority("Desenvolvedor Sênior", "vaga júnior") == "senior"
    assert detect_seniority("Tech Lead Backend") == "lideranca"
    assert detect_seniority("Desenvolvedor", "") is None


def test_enrich_fills_derived_fields():
    job = Job(
        source="t",
        external_id="1",
        title="Desenvolvedor Python Sênior (PJ) - Remoto",
        url="http://x",
        location_raw="Campinas - SP",
        description="Vaga PJ com React e AWS. R$ 12.000 a R$ 15.000",
    )
    enrich(job)
    assert (job.city, job.uf, job.region) == ("Campinas", "SP", "Sudeste")
    assert job.workplace == "remoto"
    assert job.contract == "PJ"
    assert job.seniority == "senior"
    assert job.area == "backend"
    assert {"Python", "React", "AWS"} <= set(job.tags)
    assert job.salary == "R$ 12.000 a R$ 15.000"


def test_enrich_keeps_source_values():
    job = Job(
        source="t",
        external_id="2",
        title="Dev PJ",
        url="http://x",
        contract="CLT",
        uf="rs",
    )
    enrich(job)
    assert job.contract == "CLT"
    assert job.uf == "RS"
    assert job.region == "Sul"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("2026-09-10T21:17:01.896Z", "2026-09-10"),
        ("10/08/2026", "2026-08-10"),
        ("", None),
        ("sem data", None),
    ],
)
def test_parse_date_absolute(text, expected):
    assert parse_date(text) == expected


def test_parse_date_relative():
    from datetime import date, timedelta

    assert parse_date("Hoje") == date.today().isoformat()
    assert parse_date("há 3 dias") == (date.today() - timedelta(days=3)).isoformat()


@pytest.mark.parametrize(
    "title, expected",
    [
        ("Desenvolvedor Full Stack Pleno", True),
        ("Analista de Dados", True),
        ("Engenheiro de Software", True),
        ("Analista de Suporte N2", True),
        ("Programa Projetista do Futuro | Projetos Estruturais", False),
        ("Engenheiro Civil", False),
        ("Vendedor Externo", False),
        ("Auxiliar de Limpeza", False),
    ],
)
def test_is_tech_job(title, expected):
    assert is_tech_job(title) is expected
