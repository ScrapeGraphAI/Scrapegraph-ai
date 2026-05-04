## 🚀 **Procurando uma forma ainda mais rápida e simples de fazer scraping em escala (apenas 5 linhas de código)?** Confira nossa versão aprimorada em [**ScrapeGraphAI.com**](https://scrapegraphai.com/?utm_source=github&utm_medium=readme&utm_campaign=oss_cta&utm_content=top_banner)! 🚀

---

# 🕷️ ScrapeGraphAI: Você Só Faz Scraping Uma Vez

[English](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/README.md) | [中文](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/chinese.md) | [日本語](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/japanese.md)
| [한국어](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/korean.md)
| [Русский](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/russian.md) | [Türkçe](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/turkish.md)
| [Deutsch](https://www.readme-i18n.com/ScrapeGraphAI/Scrapegraph-ai?lang=de)
| [Español](https://www.readme-i18n.com/ScrapeGraphAI/Scrapegraph-ai?lang=es)
| [français](https://www.readme-i18n.com/ScrapeGraphAI/Scrapegraph-ai?lang=fr)
| [Português](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/portuguese.md)

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/scrapegraphai?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/scrapegraphai)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen?style=for-the-badge)](https://github.com/pylint-dev/pylint)
[![Pylint](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/code-quality.yml?label=Pylint&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/code-quality.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/codeql.yml?label=CodeQL&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![](https://dcbadge.vercel.app/api/server/gkxQDAjfeX)](https://discord.gg/gkxQDAjfeX)

[![API Banner](https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/api_banner.png)](https://scrapegraphai.com/?utm_source=github&utm_medium=readme&utm_campaign=api_banner&utm_content=api_banner_image)

<p align="center">
<a href="https://trendshift.io/repositories/9761" target="_blank"><img src="https://trendshift.io/api/badge/repositories/9761" alt="VinciGit00%2FScrapegraph-ai | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
<p align="center">

[ScrapeGraphAI](https://scrapegraphai.com) é uma biblioteca Python de *web scraping* que usa LLM e lógica de grafo direto para criar pipelines de scraping para sites e documentos locais (XML, HTML, JSON, Markdown, etc.).

Basta dizer qual informação você quer extrair e a biblioteca fará isso por você!

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/sgai-hero.png" alt="ScrapeGraphAI Hero" style="width: 100%;">
</p>


## 🚀 Integrações
O ScrapeGraphAI oferece integração perfeita com frameworks e ferramentas populares para aprimorar suas capacidades de scraping. Seja você construindo com Python ou Node.js, usando frameworks LLM ou trabalhando com plataformas no-code, temos você coberto com nossas opções abrangentes de integração.

Você pode encontrar mais informações no seguinte [link](https://scrapegraphai.com)

**Integrações**:
- **API**: [Documentação](https://docs.scrapegraphai.com/introduction)
- **SDKs**: [Python](https://docs.scrapegraphai.com/sdks/python), [Node](https://docs.scrapegraphai.com/sdks/javascript)
- **Frameworks LLM**: [Langchain](https://docs.scrapegraphai.com/integrations/langchain), [Llama Index](https://docs.scrapegraphai.com/integrations/llamaindex), [Crew.ai](https://docs.scrapegraphai.com/integrations/crewai), [Agno](https://docs.scrapegraphai.com/integrations/agno), [CamelAI](https://github.com/camel-ai/camel)
- **Frameworks Low-code**: [Pipedream](https://pipedream.com/apps/scrapegraphai), [Bubble](https://bubble.io/plugin/scrapegraphai-1745408893195x213542371433906180), [Zapier](https://zapier.com/apps/scrapegraphai/integrations), [n8n](http://localhost:5001/dashboard), [Dify](https://dify.ai), [Toolhouse](https://app.toolhouse.ai/mcp-servers/scrapegraph_smartscraper)
- **Servidor MCP**:  [Link](https://smithery.ai/server/@ScrapeGraphAI/scrapegraph-mcp)

## 🚀 Instalação Rápida

A página de referência para Scrapegraph-ai está disponível na página oficial do PyPI: [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai

# IMPORTANTE (para buscar conteúdo de sites)
playwright install
```

**Nota**: é recomendado instalar a biblioteca em um ambiente virtual para evitar conflitos com outras bibliotecas 🐱


## 💻 Uso
Existem múltiplos pipelines de scraping padrão que podem ser usados para extrair informações de um site (ou arquivo local).

O mais comum é o `SmartScraperGraph`, que extrai informações de uma única página dado um prompt do usuário e uma URL de origem.


```python
from scrapegraphai.graphs import SmartScraperGraph

# Defina a configuração para o pipeline de scraping
graph_config = {
    "llm": {
        "model": "ollama/llama3.2",
        "model_tokens": 8192,
        "format": "json",
    },
    "verbose": True,
    "headless": False,
}

# Crie a instância SmartScraperGraph
smart_scraper_graph = SmartScraperGraph(
    prompt="Extraia informações úteis da página web, incluindo uma descrição do que a empresa faz, fundadores e links de redes sociais",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# Execute o pipeline
result = smart_scraper_graph.run()

import json
print(json.dumps(result, indent=4))
```

> [!NOTE]
> Para OpenAI e outros modelos, você só precisa mudar a configuração do llm!
> ```python
>graph_config = {
>    "llm": {
>        "api_key": "YOUR_OPENAI_API_KEY",
>        "model": "openai/gpt-4o-mini",
>    },
>    "verbose": True,
>    "headless": False,
>}
>```


A saída será um dicionário como o seguinte:

```python
{
    "description": "ScrapeGraphAI transforms websites into clean, organized data for AI agents and data analytics. It offers an AI-powered API for effortless and cost-effective data extraction.",
    "founders": [
        {
            "name": "",
            "role": "Founder & Technical Lead",
            "linkedin": "https://www.linkedin.com/in/perinim/"
        },
        {
            "name": "Marco Vinciguerra",
            "role": "Founder & Software Engineer",
            "linkedin": "https://www.linkedin.com/in/marco-vinciguerra-7ba365242/"
        },
        {
            "name": "Lorenzo Padoan",
            "role": "Founder & Product Engineer",
            "linkedin": "https://www.linkedin.com/in/lorenzo-padoan-4521a2154/"
        }
    ],
    "social_media_links": {
        "linkedin": "https://www.linkedin.com/company/101881123",
        "twitter": "https://x.com/scrapegraphai",
        "github": "https://github.com/ScrapeGraphAI/Scrapegraph-ai"
    }
}
```
Existem outros pipelines que podem ser usados para extrair informações de múltiplas páginas, gerar scripts Python ou até mesmo gerar arquivos de áudio.

| Nome do Pipeline           | Descrição                                                                                                      |
|-------------------------|------------------------------------------------------------------------------------------------------------------|
| SmartScraperGraph       | Scraper de página única que só precisa de um prompt do usuário e uma fonte de entrada.                                           |
| SearchGraph             | Scraper de múltiplas páginas que extrai informações dos n principais resultados de pesquisa de um mecanismo de busca.                  |
| SpeechGraph             | Scraper de página única que extrai informações de um site e gera um arquivo de áudio.                       |
| ScriptCreatorGraph      | Scraper de página única que extrai informações de um site e gera um script Python.                     |
| SmartScraperMultiGraph  | Scraper de múltiplas páginas que extrai informações de múltiplas páginas dado um único prompt e uma lista de fontes.    |
| ScriptCreatorMultiGraph | Scraper de múltiplas páginas que gera um script Python para extrair informações de múltiplas páginas e fontes.     |

Para cada um desses grafos existe a versão multi. Isso permite fazer chamadas do LLM em paralelo.

É possível usar diferentes LLMs através de APIs, como **OpenAI**, **Groq**, **Azure** e **Gemini**, ou modelos locais usando **Ollama**.

Lembre-se de ter o [Ollama](https://ollama.com/) instalado e baixar os modelos usando o comando **ollama pull**, se você quiser usar modelos locais.


## 📖 Documentação

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

A documentação do ScrapeGraphAI pode ser encontrada [aqui](https://docs.scrapegraphai.com/introduction).

## 🤝 Contribuindo

Sinta-se à vontade para contribuir e junte-se ao nosso servidor Discord para discutir melhorias e nos dar sugestões!

Por favor, veja as [diretrizes de contribuição](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/CONTRIBUTING.md).

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 🔗 ScrapeGraph API & SDKs
Se você está procurando uma solução rápida para integrar o ScrapeGraph em seu sistema, confira nossa poderosa API [aqui!](https://dashboard.scrapegraphai.com/login)

[![API Banner](https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/api_banner.png)](https://dashboard.scrapegraphai.com/login)

Oferecemos SDKs em Python e Node.js, facilitando a integração em seus projetos. Confira abaixo:

| SDK       | Linguagem | Link do GitHub                                                                 |
|-----------|----------|-----------------------------------------------------------------------------|
| Python SDK | Python   | [scrapegraph-py](https://github.com/ScrapeGraphAI/scrapegraph-sdk/tree/main/scrapegraph-py) |
| Node.js SDK | Node.js  | [scrapegraph-js](https://github.com/ScrapeGraphAI/scrapegraph-sdk/tree/main/scrapegraph-js) |

A Documentação Oficial da API pode ser encontrada [aqui](https://docs.scrapegraphai.com/introduction).

## 🔥 Benchmark

De acordo com o benchmark do Firecrawl [Firecrawl benchmark](https://github.com/firecrawl/scrape-evals/pull/3), o ScrapeGraph é o melhor fetcher do mercado!

![here](assets/histogram.png)

## 📈 Telemetria
Coletamos métricas de uso anônimas para melhorar a qualidade e a experiência do usuário do nosso pacote. Os dados nos ajudam a priorizar melhorias e garantir compatibilidade. Se você deseja optar por não participar, defina a variável de ambiente SCRAPEGRAPHAI_TELEMETRY_ENABLED=false. Para mais informações, consulte a documentação [aqui](https://docs.scrapegraphai.com/introduction).

## ❤️ Contribuidores
[![Contributors](https://contrib.rocks/image?repo=VinciGit00/Scrapegraph-ai)](https://github.com/VinciGit00/Scrapegraph-ai/graphs/contributors)

## 🎓 Citações
Se você usou nossa biblioteca para fins de pesquisa, por favor, cite-nos com a seguinte referência:
```text
  @misc{scrapegraph-ai,
    author = {Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/VinciGit00/Scrapegraph-ai},
    note = {Uma biblioteca Python para scraping aproveitando grandes modelos de linguagem}
  }
```

## Autores

|                    | Informações de Contato         |
|--------------------|----------------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/)    |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)  |

## 📜 Licença

O ScrapeGraphAI está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/LICENSE) para mais informações.

## Agradecimentos

- Gostaríamos de agradecer a todos os contribuidores do projeto e à comunidade de código aberto pelo seu apoio.
- O ScrapeGraphAI destina-se apenas a fins de exploração de dados e pesquisa. Não nos responsabilizamos por qualquer uso indevido da biblioteca.

Made with ❤️ by [ScrapeGraph AI](https://scrapegraphai.com)

[Scarf tracking](https://static.scarf.sh/a.png?x-pxid=102d4b8c-cd6a-4b9e-9a16-d6d141b9212d)
