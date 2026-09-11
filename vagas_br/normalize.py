"""Rule-based enrichment: contract type, work model, seniority, area, tags."""

from __future__ import annotations

import re

from .geo import parse_location, region_of, uf_from_city, workplace_from_text
from .models import Job

_PJ_RE = re.compile(
    r"\bPJ\b|pessoa\s+jur[ií]dica|\bCNPJ\b|contrato\s+PJ|regime\s+PJ|modelo\s+PJ|"
    r"\bMEI\b|prestador(a)?\s+de\s+servi[cç]o",
    re.I,
)
_CLT_RE = re.compile(
    r"\bCLT\b|carteira\s+assinada|regime\s+CLT|efetiv[oa]\b|contrata[cç][aã]o\s+CLT",
    re.I,
)
_ESTAGIO_RE = re.compile(r"est[aá]gi[oa]|estagi[aá]ri[oa]|\bintern(ship)?\b", re.I)
_TEMP_RE = re.compile(r"tempor[aá]ri[oa]|contrato\s+por\s+prazo\s+determinado", re.I)
_FREELA_RE = re.compile(r"freela(nce|ncer)?\b|aut[oô]nom[oa]", re.I)
_TERCEIRO_RE = re.compile(r"terceiriz|outsourc", re.I)
_APRENDIZ_RE = re.compile(r"\baprendiz\b|jovem\s+aprendiz", re.I)

_SENIORITY_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("estagio", re.compile(r"est[aá]gi|estagi[aá]ri|\bintern\b|trainee", re.I)),
    (
        "lideranca",
        re.compile(
            r"\b(tech\s*lead|team\s*lead|l[ií]der|lead\b|head\b|gerente|manager|coordenador|"
            r"coordenadora|diretor|cto\b|principal|staff)\b",
            re.I,
        ),
    ),
    (
        "especialista",
        re.compile(r"especialista|specialist|arquitet[oa]|architect|expert", re.I),
    ),
    ("senior", re.compile(r"s[eê]nior|\bsr\b|\bsenior\b|\biii\b", re.I)),
    (
        "pleno",
        re.compile(r"\bpleno\b|\bpl\b|mid-?level|\bmid\b|\bii\b|intermediate", re.I),
    ),
    ("junior", re.compile(r"j[uú]nior|\bjr\b|\bjunior\b|\bi\b|entry|iniciante", re.I)),
]

_AREA_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("fullstack", re.compile(r"full\s*-?\s*stack", re.I)),
    (
        "mobile",
        re.compile(
            r"\bmobile\b|android|\bios\b|flutter|react\s*native|kotlin|swift", re.I
        ),
    ),
    (
        "frontend",
        re.compile(
            r"front\s*-?\s*end|\bfront\b|react(?!\s*native)|angular|vue|\bui\b|web\s+designer",
            re.I,
        ),
    ),
    (
        "dados",
        re.compile(
            r"\bdados\b|\bdata\b|\bbi\b|analytics|machine\s+learning|\bml\b|\bia\b|\bai\b|"
            r"cientista|scientist|\bdba\b|banco\s+de\s+dados|etl|power\s*bi|big\s*data",
            re.I,
        ),
    ),
    (
        "devops",
        re.compile(
            r"devops|\bsre\b|cloud|plataforma|platform|kubernetes|\bk8s\b|infra(estrutura)?\s+cloud|mlops",
            re.I,
        ),
    ),
    (
        "qa",
        re.compile(
            r"\bqa\b|quality|qualidade|test(e|er|ador|ing)|automa[cç][aã]o\s+de\s+testes",
            re.I,
        ),
    ),
    ("seguranca", re.compile(r"seguran[cç]a|security|pentest|\bsoc\b|cyber", re.I)),
    (
        "erp",
        re.compile(
            r"\bsap\b|\berp\b|totvs|protheus|salesforce|dynamics|oracle\s+ebs|abap|senior\s+sistemas",
            re.I,
        ),
    ),
    (
        "suporte",
        re.compile(
            r"suporte|help\s*desk|service\s*desk|\bn[123]\b|field\s+service", re.I
        ),
    ),
    (
        "infra",
        re.compile(
            r"infra(estrutura)?|redes|network|sysadmin|servidores|datacenter|telecom",
            re.I,
        ),
    ),
    (
        "produto",
        re.compile(
            r"product\s+(owner|manager)|\bpo\b|\bpm\b|produto|ux|scrum\s*master|agilista",
            re.I,
        ),
    ),
    (
        "gestao",
        re.compile(
            r"gerente|manager|coordenador|head|diretor|\bcto\b|gest[aã]o\s+de\s+projetos|pmo",
            re.I,
        ),
    ),
    (
        "backend",
        re.compile(
            r"back\s*-?\s*end|\bapi\b|java\b|python|\.net|c#|node|golang|\bgo\b|php|ruby|rust|"
            r"elixir|scala|kotlin|spring|django|laravel|microsservi",
            re.I,
        ),
    ),
]

# Display label -> regex. Order matters only for output stability.
_TAG_RULES: list[tuple[str, re.Pattern[str]]] = [
    (label, re.compile(pattern, re.I))
    for label, pattern in [
        ("Python", r"\bpython\b"),
        ("Java", r"\bjava\b(?!\s*script)"),
        ("JavaScript", r"javascript|\bjs\b"),
        ("TypeScript", r"typescript|\bts\b"),
        ("Node.js", r"node(\.js|js)?\b"),
        ("React", r"\breact(\.js|js)?\b(?!\s*native)"),
        ("React Native", r"react\s*native"),
        ("Angular", r"\bangular"),
        ("Vue", r"\bvue(\.js|js)?\b"),
        ("Next.js", r"next\.?js"),
        (".NET", r"\.net\b|dotnet|asp\.net"),
        ("C#", r"\bc#|csharp"),
        ("C/C++", r"\bc\+\+|\bc\b\s*/\s*c\+\+"),
        ("PHP", r"\bphp\b"),
        ("Laravel", r"laravel"),
        ("Ruby", r"\bruby\b|rails"),
        ("Go", r"\bgolang\b|\bgo\b(?=\s*(dev|lang|,|/|\)|$))"),
        ("Rust", r"\brust\b"),
        ("Kotlin", r"\bkotlin\b"),
        ("Swift", r"\bswift\b"),
        ("Flutter", r"\bflutter\b"),
        ("Android", r"\bandroid\b"),
        ("iOS", r"\bios\b"),
        ("Delphi", r"\bdelphi\b"),
        ("COBOL", r"\bcobol\b"),
        ("ABAP", r"\babap\b"),
        ("SAP", r"\bsap\b"),
        ("Salesforce", r"salesforce"),
        ("TOTVS", r"totvs|protheus"),
        ("Oracle", r"\boracle\b"),
        ("SQL", r"\bsql\b|\bt-sql\b|pl/?sql"),
        ("PostgreSQL", r"postgres"),
        ("MySQL", r"mysql|mariadb"),
        ("SQL Server", r"sql\s*server"),
        ("MongoDB", r"mongo"),
        ("Redis", r"\bredis\b"),
        ("Kafka", r"\bkafka\b"),
        ("RabbitMQ", r"rabbitmq"),
        ("AWS", r"\baws\b|amazon\s+web"),
        ("Azure", r"\bazure\b"),
        ("GCP", r"\bgcp\b|google\s+cloud"),
        ("Docker", r"\bdocker\b"),
        ("Kubernetes", r"kubernetes|\bk8s\b"),
        ("Terraform", r"terraform"),
        ("Linux", r"\blinux\b"),
        ("CI/CD", r"ci/?cd|jenkins|gitlab\s*ci|github\s*actions"),
        ("Spring", r"\bspring\b"),
        ("Django", r"\bdjango\b"),
        ("FastAPI", r"fastapi"),
        ("Flask", r"\bflask\b"),
        ("GraphQL", r"graphql"),
        ("REST", r"\brest(ful)?\b"),
        ("Microsserviços", r"micro\s*-?servi|microservice"),
        ("Machine Learning", r"machine\s+learning|\bml\b|deep\s+learning"),
        ("IA/LLM", r"\bia\b|\bai\b|\bllm|gen(erative)?\s*ai|langchain|openai"),
        ("Data Science", r"data\s+scien|cientista\s+de\s+dados"),
        (
            "Data Engineering",
            r"data\s+engineer|engenh\w+\s+de\s+dados|spark|databricks|airflow",
        ),
        ("Power BI", r"power\s*bi"),
        ("Scrum/Agile", r"\bscrum\b|\bagile\b|\bágil\b|kanban"),
        ("QA/Testes", r"\bqa\b|selenium|cypress|playwright|testes?\s+automatizad"),
        ("Segurança", r"seguran[cç]a\s+da\s+informa|cyber|pentest|\bsoc\b"),
        ("Low-code", r"low-?code|outsystems|power\s*apps|mendix"),
        ("WordPress", r"wordpress"),
        ("Shopify/VTEX", r"shopify|vtex|magento"),
        ("Unity/Games", r"\bunity\b|unreal|game\s*dev"),
        ("Embarcados", r"embarcad|embedded|firmware|iot\b"),
    ]
]

_SALARY_RE = re.compile(
    r"(R\$\s?\d{1,3}(\.\d{3})*(,\d{2})?(\s?(a|-|até)\s?R\$\s?\d{1,3}(\.\d{3})*(,\d{2})?)?)"
)


def detect_contract(text: str) -> str | None:
    """Detect the contract type from free text."""
    if not text:
        return None
    pj = bool(_PJ_RE.search(text))
    clt = bool(_CLT_RE.search(text))
    if pj and clt:
        return "CLT/PJ"
    if pj:
        return "PJ"
    if clt:
        return "CLT"
    if _APRENDIZ_RE.search(text):
        return "APRENDIZ"
    if _ESTAGIO_RE.search(text):
        return "ESTAGIO"
    if _TEMP_RE.search(text):
        return "TEMPORARIO"
    if _FREELA_RE.search(text):
        return "FREELANCE"
    if _TERCEIRO_RE.search(text):
        return "TERCEIRIZADO"
    return None


def detect_seniority(title: str, text: str = "") -> str | None:
    """Detect seniority, preferring the title over the body."""
    for level, rx in _SENIORITY_RULES:
        if rx.search(title or ""):
            return level
    for level, rx in _SENIORITY_RULES:
        if level in {"estagio", "senior", "pleno", "junior"} and rx.search(text or ""):
            return level
    return None


def detect_area(title: str) -> str:
    """Classify the job area from its title."""
    for area, rx in _AREA_RULES:
        if rx.search(title or ""):
            return area
    return "outro"


def detect_tags(text: str) -> list[str]:
    """Return the technology tags mentioned in the text."""
    if not text:
        return []
    return [label for label, rx in _TAG_RULES if rx.search(text)]


def detect_salary(text: str) -> str | None:
    """Return the first ``R$`` amount / range found."""
    m = _SALARY_RE.search(text or "")
    return m.group(1).strip() if m else None


def enrich(job: Job) -> Job:
    """Fill in derived fields without overriding what the source provided."""
    text = job.text
    if job.location_raw and (not job.uf or not job.city):
        loc = parse_location(job.location_raw)
        job.city = job.city or loc["city"]
        job.uf = job.uf or loc["uf"]
        job.workplace = job.workplace or loc["workplace"]
    if job.city and not job.uf:
        job.uf = uf_from_city(job.city)
    if job.uf:
        job.uf = job.uf.upper()
        job.region = job.region or region_of(job.uf)
    if not job.workplace:
        job.workplace = workplace_from_text(job.title) or workplace_from_text(
            job.description or ""
        )
    if not job.contract:
        job.contract = detect_contract(text)
    if not job.seniority:
        job.seniority = detect_seniority(job.title, job.description or "")
    if not job.area:
        job.area = detect_area(job.title)
    found = detect_tags(text)
    job.tags = sorted(set(job.tags) | set(found))
    if not job.salary:
        job.salary = detect_salary(job.description or "")
    job.title = " ".join(job.title.split())
    if job.company:
        job.company = " ".join(job.company.split())
    return job


_TECH_TITLE_RE = re.compile(
    r"desenvolv|develop|programad|programm|software|dev|back\s*-?end|front\s*-?end|"
    r"full\s*-?stack|mobile|android|ios|flutter|devops|sre|cloud|dados|data|"
    r"cientista|scientist|machine\s+learning|ml|ia|ai|bi|analytics|"
    r"qa|tester|testes?|qualidade\s+de\s+software|automa[cç][aã]o\s+de\s+testes|"
    r"sistemas?|ti|tecnologia|tech|engineer|engenheir[oa]\s+(de\s+)?(software|dados|"
    r"computa|ml|machine|devops|cloud|plataforma|platform|sistemas|telecom|redes|ia|ai)|"
    r"arquitet[oa]\s+(de\s+)?(solu|software|dados|sistemas|cloud|nuvem)|dba|banco\s+de\s+dados|"
    r"sap|abap|salesforce|totvs|protheus|erp|scrum|agil|product\s+(owner|manager)|"
    r"po|ux|ui|cyber|seguran[cç]a\s+da\s+informa|infosec|pentest|soc|"
    r"infraestrutura|infra|redes|network|suporte\s+(t[eé]cnico|ti|n[123]|de\s+ti)|help\s*desk|"
    r"service\s*desk|sysadmin|linux|windows\s+server|datacenter|telecom|python|java|\.net|"
    r"c#|php|node|react|angular|vue|kotlin|swift|golang|rust|ruby|delphi|cobol|oracle|sql|"
    r"aws|azure|gcp|kubernetes|docker|low-?code|power\s*(bi|apps|platform)|rpa|"
    r"analista\s+de\s+(sistemas|ti|suporte|infra|bi|dados|qualidade|testes|seguran|redes|"
    r"banco|requisitos|neg[oó]cios?\s+ti|implanta|integra|erp|sap|crm)|"
    r"tech\s*lead|team\s*lead|coordenador\w*\s+de\s+(ti|tecnologia|desenvolvimento|sistemas)|"
    r"gerente\s+de\s+(ti|tecnologia|projetos\s+de\s+ti|desenvolvimento|engenharia)|cto|"
    r"web\s*(designer|master)|wordpress|e-?commerce|games?|unity|embarcad|firmware|iot|"
    r"automa[cç][aã]o\s+(industrial|de\s+processos)|clp|plc",
    re.I,
)
_NON_TECH_TITLE_RE = re.compile(
    r"engenheir[oa]\s+(civil|mec[aâ]nic|el[eé]tric|eletr[oô]nic|de\s+produ[cç]|qu[ií]mic|"
    r"agr[oô]nom|ambiental|de\s+seguran[cç]a\s+do\s+trabalho|de\s+minas|naval|florestal)|"
    r"projetista|estrutura(l|is)|pedreiro|motorista|vendedor|auxiliar\s+de\s+(limpeza|produ|"
    r"cozinha|log[ií]stica|escrit[oó]rio)|enfermeir|m[eé]dic[oa]|farmac|contador|"
    r"advogad|recepcionista|operador\s+de\s+(caixa|m[aá]quina|empilhadeira)|professor(a)?\s+de\s+"
    r"(matem|portugu|ingl|hist|geograf|f[ií]sica|qu[ií]mica|educa)|estoquista|"
    r"repositor|garçom|garcom|cozinheir|seguran[cç]a\s+patrimonial|vigilante|porteiro",
    re.I,
)


def is_tech_job(title: str) -> bool:
    """True when the title looks like a technology / software role.

    Query-based boards return fuzzy matches (e.g. civil-engineering jobs for
    "engenheiro"); this keeps the aggregator focused on tech openings.
    """
    if not title:
        return False
    if _NON_TECH_TITLE_RE.search(title) and not re.search(
        r"desenvolv|software|program|dev|dados|ti|sistemas", title, re.I
    ):
        return False
    return bool(_TECH_TITLE_RE.search(title))
