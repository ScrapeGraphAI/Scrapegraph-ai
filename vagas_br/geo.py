"""Brazilian geography helpers: UFs, regions and location parsing."""

from __future__ import annotations

import re
import unicodedata

# UF -> (state name, region)
UFS: dict[str, tuple[str, str]] = {
    "AC": ("Acre", "Norte"),
    "AL": ("Alagoas", "Nordeste"),
    "AP": ("Amapá", "Norte"),
    "AM": ("Amazonas", "Norte"),
    "BA": ("Bahia", "Nordeste"),
    "CE": ("Ceará", "Nordeste"),
    "DF": ("Distrito Federal", "Centro-Oeste"),
    "ES": ("Espírito Santo", "Sudeste"),
    "GO": ("Goiás", "Centro-Oeste"),
    "MA": ("Maranhão", "Nordeste"),
    "MT": ("Mato Grosso", "Centro-Oeste"),
    "MS": ("Mato Grosso do Sul", "Centro-Oeste"),
    "MG": ("Minas Gerais", "Sudeste"),
    "PA": ("Pará", "Norte"),
    "PB": ("Paraíba", "Nordeste"),
    "PR": ("Paraná", "Sul"),
    "PE": ("Pernambuco", "Nordeste"),
    "PI": ("Piauí", "Nordeste"),
    "RJ": ("Rio de Janeiro", "Sudeste"),
    "RN": ("Rio Grande do Norte", "Nordeste"),
    "RS": ("Rio Grande do Sul", "Sul"),
    "RO": ("Rondônia", "Norte"),
    "RR": ("Roraima", "Norte"),
    "SC": ("Santa Catarina", "Sul"),
    "SP": ("São Paulo", "Sudeste"),
    "SE": ("Sergipe", "Nordeste"),
    "TO": ("Tocantins", "Norte"),
}

REGIONS: list[str] = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

# Capitals and other large / tech-relevant cities -> UF (accent-stripped keys).
CITY_UF: dict[str, str] = {
    # capitals
    "rio branco": "AC",
    "maceio": "AL",
    "macapa": "AP",
    "manaus": "AM",
    "salvador": "BA",
    "fortaleza": "CE",
    "brasilia": "DF",
    "vitoria": "ES",
    "goiania": "GO",
    "sao luis": "MA",
    "cuiaba": "MT",
    "campo grande": "MS",
    "belo horizonte": "MG",
    "belem": "PA",
    "joao pessoa": "PB",
    "curitiba": "PR",
    "recife": "PE",
    "teresina": "PI",
    "rio de janeiro": "RJ",
    "natal": "RN",
    "porto alegre": "RS",
    "porto velho": "RO",
    "boa vista": "RR",
    "florianopolis": "SC",
    "sao paulo": "SP",
    "aracaju": "SE",
    "palmas": "TO",
    # SP
    "campinas": "SP",
    "sao jose dos campos": "SP",
    "ribeirao preto": "SP",
    "sorocaba": "SP",
    "santos": "SP",
    "sao bernardo do campo": "SP",
    "santo andre": "SP",
    "osasco": "SP",
    "barueri": "SP",
    "guarulhos": "SP",
    "sao caetano do sul": "SP",
    "jundiai": "SP",
    "piracicaba": "SP",
    "bauru": "SP",
    "sao jose do rio preto": "SP",
    "presidente prudente": "SP",
    "limeira": "SP",
    "americana": "SP",
    "indaiatuba": "SP",
    "franca": "SP",
    "marilia": "SP",
    "taubate": "SP",
    "mogi das cruzes": "SP",
    "alphaville": "SP",
    "sao carlos": "SP",
    "araraquara": "SP",
    "diadema": "SP",
    "cotia": "SP",
    "itu": "SP",
    "valinhos": "SP",
    "vinhedo": "SP",
    "hortolandia": "SP",
    "paulinia": "SP",
    "sumare": "SP",
    "botucatu": "SP",
    "itatiba": "SP",
    "santana de parnaiba": "SP",
    "sao vicente": "SP",
    "praia grande": "SP",
    "aracatuba": "SP",
    "rio claro": "SP",
    "jacarei": "SP",
    "atibaia": "SP",
    # RJ
    "niteroi": "RJ",
    "petropolis": "RJ",
    "duque de caxias": "RJ",
    "nova iguacu": "RJ",
    "macae": "RJ",
    "volta redonda": "RJ",
    "campos dos goytacazes": "RJ",
    "sao goncalo": "RJ",
    "resende": "RJ",
    # MG
    "uberlandia": "MG",
    "juiz de fora": "MG",
    "contagem": "MG",
    "betim": "MG",
    "nova lima": "MG",
    "uberaba": "MG",
    "montes claros": "MG",
    "pocos de caldas": "MG",
    "divinopolis": "MG",
    "ipatinga": "MG",
    "sete lagoas": "MG",
    "vicosa": "MG",
    "itajuba": "MG",
    "santa rita do sapucai": "MG",
    "varginha": "MG",
    "pouso alegre": "MG",
    "governador valadares": "MG",
    # ES
    "vila velha": "ES",
    "serra": "ES",
    "cariacica": "ES",
    "cachoeiro de itapemirim": "ES",
    "viana": "ES",
    "linhares": "ES",
    # PR
    "londrina": "PR",
    "maringa": "PR",
    "cascavel": "PR",
    "ponta grossa": "PR",
    "foz do iguacu": "PR",
    "sao jose dos pinhais": "PR",
    "pinhais": "PR",
    "colombo": "PR",
    "pato branco": "PR",
    "toledo": "PR",
    "araucaria": "PR",
    "guarapuava": "PR",
    "apucarana": "PR",
    # SC
    "joinville": "SC",
    "blumenau": "SC",
    "sao jose": "SC",
    "chapeco": "SC",
    "itajai": "SC",
    "criciuma": "SC",
    "jaragua do sul": "SC",
    "palhoca": "SC",
    "balneario camboriu": "SC",
    "lages": "SC",
    "brusque": "SC",
    "tubarao": "SC",
    "rio do sul": "SC",
    "concordia": "SC",
    "navegantes": "SC",
    # RS
    "caxias do sul": "RS",
    "canoas": "RS",
    "novo hamburgo": "RS",
    "pelotas": "RS",
    "santa maria": "RS",
    "sao leopoldo": "RS",
    "gravatai": "RS",
    "passo fundo": "RS",
    "bento goncalves": "RS",
    "lajeado": "RS",
    "erechim": "RS",
    "marau": "RS",
    "rio grande": "RS",
    # NE
    "campina grande": "PB",
    "feira de santana": "BA",
    "caruaru": "PE",
    "jaboatao dos guararapes": "PE",
    "olinda": "PE",
    "petrolina": "PE",
    "carpina": "PE",
    "sobral": "CE",
    "juazeiro do norte": "CE",
    "mossoro": "RN",
    "vitoria da conquista": "BA",
    "ilheus": "BA",
    "lauro de freitas": "BA",
    "parnamirim": "RN",
    "imperatriz": "MA",
    "patos": "PB",
    "eusebio": "CE",
    # CO
    "anapolis": "GO",
    "aparecida de goiania": "GO",
    "rio verde": "GO",
    "dourados": "MS",
    "rondonopolis": "MT",
    "sinop": "MT",
    "varzea grande": "MT",
    "taguatinga": "DF",
    "aguas claras": "DF",
    # N
    "ananindeua": "PA",
    "santarem": "PA",
    "maraba": "PA",
    "araguaina": "TO",
    "ji-parana": "RO",
    "ji parana": "RO",
}


def strip_accents(text: str) -> str:
    """Lower-case and remove accents (``São Paulo`` -> ``sao paulo``)."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


STATE_NAME_TO_UF: dict[str, str] = {
    strip_accents(name): uf for uf, (name, _) in UFS.items()
}
# Aliases seen on job boards (LinkedIn uses English names).
STATE_NAME_TO_UF.update(
    {
        "federal district": "DF",
        "state of sao paulo": "SP",
        "state of rio de janeiro": "RJ",
        "state of minas gerais": "MG",
        "state of parana": "PR",
        "state of santa catarina": "SC",
        "state of rio grande do sul": "RS",
        "state of goias": "GO",
        "state of bahia": "BA",
        "state of ceara": "CE",
        "state of pernambuco": "PE",
        "state of espirito santo": "ES",
        "greater sao paulo area": "SP",
        "greater rio de janeiro area": "RJ",
        "greater belo horizonte area": "MG",
        "greater curitiba area": "PR",
        "greater porto alegre area": "RS",
        "greater florianopolis area": "SC",
        "greater recife area": "PE",
        "greater brasilia area": "DF",
        "greater campinas area": "SP",
        "greater fortaleza area": "CE",
        "greater salvador area": "BA",
        "greater goiania area": "GO",
    }
)

_UF_TOKEN_RE = re.compile(r"(?<![A-Za-z])(" + "|".join(UFS) + r")(?![A-Za-z])")
_REMOTE_RE = re.compile(
    r"\b(remot[oa]|home\s*office|100%\s*remoto|anywhere|trabalho remoto|remote)\b",
    re.I,
)
_HYBRID_RE = re.compile(r"h[ií]brid[oa]|hybrid", re.I)
_PRESENCIAL_RE = re.compile(r"\bpresencial\b|\bon-?site\b", re.I)
_NOISE_RE = re.compile(
    r"\s+e\s+regi[aã]o\b|\bregi[aã]o\s+metropolitana\s+d[eao]s?\b|^\s*grande\s+(?=\w)|"
    r"\d+\s*km\s+de\s+voc[eê]\.?|\bmetropolitan\s+area\b|\barea\b",
    re.I,
)
_ALPHA_RE = re.compile(r"[A-Za-zÀ-ÿ]")
_DIGIT_RE = re.compile(r"[\d%]")
_COUNTRY_TOKENS = {"brasil", "brazil", "br", ""}
_WORKPLACE_TOKENS = {
    "remoto",
    "remota",
    "home office",
    "remote",
    "hibrido",
    "presencial",
}


_SMALL_WORDS = {"de", "do", "da", "dos", "das", "e", "d"}


def title_case(text: str) -> str:
    """Title-case a Portuguese place name keeping connectives lower-case."""
    words = text.strip().split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i > 0 and lw in _SMALL_WORDS:
            out.append(lw)
        else:
            out.append(lw[:1].upper() + lw[1:])
    return " ".join(out)


def region_of(uf: str | None) -> str | None:
    """Return the region for a UF, or ``None``."""
    if not uf:
        return None
    entry = UFS.get(uf.upper())
    return entry[1] if entry else None


def state_name(uf: str | None) -> str | None:
    """Return the full state name for a UF."""
    if not uf:
        return None
    entry = UFS.get(uf.upper())
    return entry[0] if entry else None


def uf_from_state_name(name: str | None) -> str | None:
    """Map a state name (``Minas Gerais``) or UF (``MG``) to the UF code."""
    if not name:
        return None
    raw = name.strip()
    if raw.upper() in UFS:
        return raw.upper()
    return STATE_NAME_TO_UF.get(strip_accents(raw))


def uf_from_city(city: str | None) -> str | None:
    """Best-effort city -> UF lookup for known Brazilian cities."""
    if not city:
        return None
    return CITY_UF.get(strip_accents(city))


def workplace_from_text(text: str | None) -> str | None:
    """Detect ``remoto`` / ``hibrido`` / ``presencial`` in free text."""
    if not text:
        return None
    if _REMOTE_RE.search(text):
        return "remoto"
    if _HYBRID_RE.search(text):
        return "hibrido"
    if _PRESENCIAL_RE.search(text):
        return "presencial"
    return None


def parse_location(text: str | None) -> dict[str, str | None]:
    """Parse a free-form location string into ``city``, ``uf`` and ``workplace``.

    Handles common Brazilian board formats::

        "Belo Horizonte / MG"         -> city=Belo Horizonte, uf=MG
        "Curitiba - PR"               -> city=Curitiba, uf=PR
        "Campinas, São Paulo, Brazil" -> city=Campinas, uf=SP
        "Paraná"                      -> uf=PR
        "Remoto" / "Home office"      -> workplace=remoto
        "Brazil" / "Brasil"           -> nothing (country only)
    """
    result: dict[str, str | None] = {"city": None, "uf": None, "workplace": None}
    if not text:
        return result
    raw = " ".join(text.split())
    result["workplace"] = workplace_from_text(raw)

    # Explicit UF token, e.g. "Curitiba - PR", "São Paulo/SP", "(SP)".
    m = _UF_TOKEN_RE.search(raw)
    if m:
        result["uf"] = m.group(1)

    # Drop workplace words and parenthesised UFs before splitting into parts.
    cleaned = _REMOTE_RE.sub(" ", raw)
    cleaned = _HYBRID_RE.sub(" ", cleaned)
    cleaned = _PRESENCIAL_RE.sub(" ", cleaned)
    cleaned = _NOISE_RE.sub(" ", cleaned)
    cleaned = re.sub(r"\(([^)]*)\)", r", \1,", cleaned)
    parts = [p.strip(" -.") for p in re.split(r"[,/|–—]|\s-\s", cleaned)]
    parts = [p for p in parts if p and strip_accents(p) not in _COUNTRY_TOKENS]

    for part in parts:
        norm = strip_accents(part)
        if (
            norm in _WORKPLACE_TOKENS
            or not _ALPHA_RE.search(part)
            or _DIGIT_RE.search(part)
        ):
            continue
        if len(part) == 2 and part.upper() in UFS:
            continue
        uf = uf_from_state_name(part)
        city_uf = uf_from_city(part)
        if city_uf:
            # Prefer the city reading ("São Paulo" is both city and state).
            result["city"] = result["city"] or title_case(part)
            result["uf"] = result["uf"] or city_uf
        elif uf:
            result["uf"] = result["uf"] or uf
        elif not result["city"] and len(part) > 2:
            result["city"] = title_case(part)

    # "Rio Grande do Sul" alone must not become a city.
    if (
        result["city"]
        and strip_accents(result["city"]) in STATE_NAME_TO_UF
        and not uf_from_city(result["city"])
    ):
        result["city"] = None
    return result
