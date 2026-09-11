# Vagas Tech Brasil

Agregador de vagas de tecnologia no Brasil (CLT e PJ) construído sobre o
ScrapeGraphAI. Coleta vagas de vários portais, normaliza cidade / UF / região,
tipo de contrato, modelo de trabalho, senioridade, área e tecnologias, guarda
tudo em SQLite e serve uma página com filtros e link direto para cada vaga.

## Fontes

| Fonte        | Tipo                    | Precisa de LLM | Observações                                   |
|--------------|-------------------------|----------------|-----------------------------------------------|
| Gupy         | API JSON pública        | não            | maior ATS do Brasil; CLT/PJ e modelo vêm prontos |
| LinkedIn     | busca guest (HTML)      | não            | filtrada por `geoId` Brasil, últimos 30 dias   |
| Programathor | HTML                    | não            | só vagas dev; contrato e senioridade explícitos |
| InfoJobs     | HTML                    | não            | página nacional + uma página por estado        |
| Vagas.com    | HTML                    | não            |                                                |
| Remotar, Coodesh, APInfo | `SmartScraperGraph` (Playwright + LLM) | **sim** | fonte `sgai`; sites renderizados em JS |

Fontes sem LLM formam o grupo `core` (padrão). A fonte `sgai` usa o
ScrapeGraphAI com o modelo definido em `VAGAS_LLM_MODEL`
(padrão `google_genai/gemini-2.5-flash`) e a chave em `GEMINI_API_KEY`
(ou `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GROQ_API_KEY`, `MISTRAL_API_KEY`,
ou `ollama/<modelo>` sem chave). Novos alvos podem ser adicionados em
`vagas_br/sources/sgai.py` (`DEFAULT_TARGETS`).

## Instalação

```bash
uv sync --group vagas
uv run playwright install chromium   # só para a fonte sgai
```

## Coletar vagas

```bash
uv run --group vagas python -m vagas_br.scrape                 # fontes core, termos padrão
uv run --group vagas python -m vagas_br.scrape -s gupy,linkedin -p 3
uv run --group vagas python -m vagas_br.scrape -q "engenheiro de dados" -q devops
uv run --group vagas python -m vagas_br.scrape -s all           # inclui fontes LLM
uv run --group vagas python -m vagas_br.scrape --deactivate     # marca vagas sumidas como inativas
```

Opções: `-s/--sources` (`core`, `llm`, `all` ou lista), `-q/--query`
(repetível), `-p/--pages` (páginas por termo/fonte, padrão 5), `--db`
(caminho do SQLite, padrão `vagas_br/data/vagas.db`), `--all-titles`
(desliga o filtro que descarta títulos que não parecem cargo de tecnologia,
ex.: "Engenheiro Civil" vindo da busca por "engenheiro"), `-v`.

Os termos padrão cobrem desenvolvedor, developer, programador, engenheiro de
software, backend, frontend, full stack, mobile, devops, sre, cloud, dados,
data engineer, cientista de dados, machine learning, qa, analista de sistemas,
arquiteto de software, suporte, infraestrutura, segurança, tech lead, product
owner.

## Servir a página

```bash
uv run --group vagas uvicorn vagas_br.api:app --port 8000
```

Abra <http://localhost:8000>. Filtros: busca livre, contrato (CLT / PJ /
CLT ou PJ / estágio / ...), modelo (remoto / híbrido / presencial), região,
UF, cidade, senioridade, área, tecnologias, fonte e data de publicação. Os
filtros ficam na URL (`#...`), então podem ser compartilhados.

### API

- `GET /api/jobs?q=&uf=SP&uf=RJ&regiao=Sul&contrato=PJ&modelo=remoto&senioridade=senior&area=backend&tag=Python&fonte=gupy&cidade=Campinas&dias=7&page=1&per_page=50&order=recent`
- `GET /api/facets?...` mesmos filtros; devolve contagem por valor.
- `GET /api/meta` listas de UFs/regiões/valores e status das últimas coletas.

## Como a normalização funciona

- **Localização**: `geo.parse_location` entende `Cidade / UF`, `Cidade - UF`,
  `Cidade, Estado, Brazil`, nome do estado sozinho, `Remoto`, `Home office`;
  cidades conhecidas (capitais e polos) resolvem a UF mesmo sem sigla.
- **Contrato**: valor da fonte quando existe (Gupy, Programathor); senão regex
  em título/descrição (`PJ`, `CNPJ`, `pessoa jurídica`, `CLT`, `carteira
  assinada`, estágio, temporário, freelance...). Sem indício fica vazio.
- **Modelo, senioridade, área, tags, salário**: regras em `normalize.py`.

Vagas sem UF são remotas, nacionais ou sem local informado. Use o filtro
**Modelo = Remoto** para vê-las.

## Agendar

Rodar a coleta periodicamente (ex.: cron / Agendador de Tarefas do Windows):

```
uv run --group vagas python -m vagas_br.scrape --deactivate
```
