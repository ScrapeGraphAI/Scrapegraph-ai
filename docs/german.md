## 🚀 **Suchen Sie nach einem noch schnelleren und einfacheren Weg, um im großen Maßstab zu scrapen (nur 5 Codezeilen)?** Schauen Sie sich unsere erweiterte Version auf [**ScrapeGraphAI.com**](https://scrapegraphai.com/?utm_source=github&utm_medium=readme&utm_campaign=oss_cta&utm_content=top_banner) an! 🚀

---

# 🕷️ ScrapeGraphAI: You Only Scrape Once

<p align="center">
  <a href="https://scrapegraphai.com">
    <img src="https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/media/banner.png" alt="ScrapeGraphAI" style="width: 100%;">
  </a>
</p>

[English](../README.md) | [中文](chinese.md) | [日本語](japanese.md)
| [한국어](korean.md)
| [Русский](russian.md) | [Türkçe](turkish.md)
| [Deutsch](german.md)
| [Español](spanish.md)
| [français](french.md)
| [Português](portuguese.md)
| [Italiano](italian.md)

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/scrapegraphai?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/scrapegraphai)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![](https://dcbadge.vercel.app/api/server/gkxQDAjfeX)](https://discord.gg/gkxQDAjfeX)

<p align="center">
<a href="https://trendshift.io/repositories/15078" target="_blank"><img src="https://trendshift.io/api/badge/repositories/15078" alt="ScrapeGraphAI%2FScrapegraph-ai | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
<p align="center">

[ScrapeGraphAI](https://scrapegraphai.com) ist eine Python-Bibliothek für *Web-Scraping*, die LLM- und direkte Graphenlogik verwendet, um Scraping-Pipelines für Websites und lokale Dokumente (XML, HTML, JSON, Markdown usw.) zu erstellen.

Sagen Sie einfach, welche Informationen Sie extrahieren möchten, und die Bibliothek erledigt das für Sie!

<p align="center">
  <img src="https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/sgai-hero.png" alt="ScrapeGraphAI Hero" style="width: 100%;">
</p>

## 🚀 Integrationen

ScrapeGraphAI bietet eine nahtlose Integration mit gängigen Frameworks und Tools, um Ihre Scraping-Fähigkeiten zu erweitern. Egal, ob Sie mit Python oder Node.js entwickeln, LLM-Frameworks verwenden oder mit No-Code-Plattformen arbeiten, wir decken alles mit unseren umfassenden Integrationsmöglichkeiten ab.

Weitere Informationen finden Sie unter folgendem [Link](https://scrapegraphai.com)

**Integrationen**:
- **API**: [Dokumentation](https://docs.scrapegraphai.com/introduction)
- **SDKs**: [Python](https://docs.scrapegraphai.com/sdks/python), [Node](https://docs.scrapegraphai.com/sdks/javascript)
- **LLM-Frameworks**: [Langchain](https://docs.scrapegraphai.com/integrations/langchain), [Llama Index](https://docs.scrapegraphai.com/integrations/llamaindex), [Crew.ai](https://docs.scrapegraphai.com/integrations/crewai), [Agno](https://docs.scrapegraphai.com/integrations/agno), [CamelAI](https://github.com/camel-ai/camel)
- **Low-Code-Frameworks**: [Pipedream](https://pipedream.com/apps/scrapegraphai), [Bubble](https://bubble.io/plugin/scrapegraphai-1745408893195x213542371433906180), [Zapier](https://zapier.com/apps/scrapegraphai/integrations), [n8n](http://localhost:5001/dashboard), [Dify](https://dify.ai), [Toolhouse](https://app.toolhouse.ai/mcp-servers/scrapegraph_smartscraper)
- **MCP-Server**:  [Link](https://smithery.ai/server/@ScrapeGraphAI/scrapegraph-mcp)

## 🚀 Schnelle Installation

Die Referenzseite für Scrapegraph-ai finden Sie auf der offiziellen PyPI-Seite: [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai

# WICHTIG (für das Abrufen von Website-Inhalten)
playwright install
```

**Hinweis**: Es wird empfohlen, die Bibliothek in einer virtuellen Umgebung zu installieren, um Konflikte mit anderen Bibliotheken zu vermeiden 🐱

## 💻 Verwendung
Es gibt mehrere Standard-Scraping-Pipelines, mit denen Informationen aus einer Website (oder lokalen Datei) extrahiert werden können.

Die häufigste ist der `SmartScraperGraph`, der anhand einer Benutzereingabe und einer Quell-URL Informationen aus einer einzelnen Seite extrahiert.

```python
from scrapegraphai.graphs import SmartScraperGraph

# Definieren Sie die Konfiguration für die Scraping-Pipeline
graph_config = {
    "llm": {
        "model": "ollama/llama3.2",
        "model_tokens": 8192,
        "format": "json",
    },
    "verbose": True,
    "headless": False,
}

# Erstellen Sie die SmartScraperGraph-Instanz
smart_scraper_graph = SmartScraperGraph(
    prompt="Extract useful information from the webpage, including a description of what the company does, founders and social media links",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# Führen Sie die Pipeline aus
result = smart_scraper_graph.run()

import json
print(json.dumps(result, indent=4))
```

> [!NOTE]
> Für OpenAI und andere Modelle müssen Sie lediglich die LLM-Konfiguration ändern!
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

Die Ausgabe ist ein Wörterbuch wie folgt:

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
Es gibt weitere Pipelines, mit denen Informationen aus mehreren Seiten extrahiert, Python-Skripte generiert oder sogar Audiodateien generiert werden können.

| Pipeline Name           | Beschreibung                                                                                                      |
|-------------------------|-------------------------------------------------------------------------------------------------------------------|
| SmartScraperGraph       | Single-Page-Scraper, der nur eine Benutzereingabe und eine Eingabequelle benötigt.                               |
| SearchGraph             | Multi-Page-Scraper, der Informationen aus den oberen n Suchergebnissen einer Suchmaschine extrahiert.             |
| SpeechGraph             | Single-Page-Scraper, der Informationen aus einer Website extrahiert und eine Audiodatei generiert.               |
| ScriptCreatorGraph      | Single-Page-Scraper, der Informationen aus einer Website extrahiert und ein Python-Skript generiert.             |
| SmartScraperMultiGraph  | Multi-Page-Scraper, der Informationen aus mehreren Seiten mit einer Eingabe und einer Liste von Quellen extrahiert.|
| ScriptCreatorMultiGraph | Multi-Page-Scraper, der ein Python-Skript zum Extrahieren von Informationen aus mehreren Seiten und Quellen generiert.|

Für jeden dieser Graphen gibt es die Multi-Version. Sie ermöglicht parallele Aufrufe des LLM.

Es ist möglich, verschiedene LLMs über APIs wie **OpenAI**, **Groq**, **Azure**, **Gemini**, **MiniMax** und andere zu verwenden, oder lokale Modelle über **Ollama**.

Denken Sie daran, [Ollama](https://ollama.com/) installiert zu haben und die Modelle mit dem Befehl **ollama pull** herunterzuladen, wenn Sie lokale Modelle verwenden möchten.

## 📖 Dokumentation

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

Die Dokumentation zu ScrapeGraphAI finden Sie [hier](https://docs.scrapegraphai.com/introduction).

## 🤝 Mitwirken

Fühlen Sie sich frei, beizutragen und treten Sie unserem Discord-Server bei, um mit uns über Verbesserungen zu diskutieren und uns Vorschläge zu machen!

Bitte lesen Sie die [Richtlinien für Mitwirkende](https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/CONTRIBUTING.md).

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 🔗 ScrapeGraph API & SDKs
Wenn Sie nach einer schnellen Lösung zur Integration von ScrapeGraph in Ihr System suchen, sehen Sie sich unsere leistungsstarke API [hier!](https://dashboard.scrapegraphai.com/login) an.

[![API Banner](https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/api_banner.png)](https://dashboard.scrapegraphai.com/login)

Wir bieten SDKs für Python und Node.js an, die eine einfache Integration in Ihre Projekte ermöglichen. Sehen Sie sie sich unten an:

| SDK       | Sprache | GitHub Link                                                                 |
|-----------|----------|-----------------------------------------------------------------------------|
| Python SDK | Python   | [scrapegraph-py](https://docs.scrapegraphai.com/sdks/python) |
| Node.js SDK | Node.js  | [scrapegraph-js](https://docs.scrapegraphai.com/sdks/javascript) |

Die offizielle API-Dokumentation finden Sie [hier](https://docs.scrapegraphai.com/introduction).

## 🔥 Benchmark

Laut dem Benchmark von Firecrawl [Firecrawl benchmark](https://scrapegraphai.com/compare/firecrawl) ist ScrapeGraph der beste Fetcher auf dem Markt!

![here](assets/histogram.png)

## 📈 Telemetrie
Wir erfassen anonyme Nutzungsmetriken, um die Qualität unseres Pakets und das Benutzererlebnis zu verbessern. Die Daten helfen uns, Verbesserungen zu priorisieren und die Kompatibilität sicherzustellen. Wenn Sie dies nicht möchten, setzen Sie die Umgebungsvariable SCRAPEGRAPHAI_TELEMETRY_ENABLED=false. Weitere Informationen finden Sie in der Dokumentation [hier](https://docs.scrapegraphai.com/introduction).

## ❤️ Mitwirkende
[![Contributors](https://contrib.rocks/image?repo=ScrapeGraphAI/Scrapegraph-ai)](https://github.com/ScrapeGraphAI/Scrapegraph-ai/graphs/contributors)

## 🎓 Zitate
Wenn Sie unsere Bibliothek für Forschungszwecke verwendet haben, zitieren Sie uns bitte mit folgendem Hinweis:
```text
  @misc{scrapegraph-ai,
    author = {Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/ScrapeGraphAI/Scrapegraph-ai},
    note = {A Python library for scraping leveraging large language models}
  }
```
## Autoren

|                    | Kontakt Info         |
|--------------------|----------------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/)    |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)  |

## 📜 Lizenz

ScrapeGraphAI ist unter der MIT-Lizenz lizenziert. Weitere Informationen finden Sie in der Datei [LICENSE](https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/LICENSE).

## Danksagungen

- Wir möchten allen Mitwirkenden am Projekt und der Open-Source-Community für ihre Unterstützung danken.
- ScrapeGraphAI ist nur für Datenexploration und Forschungszwecke vorgesehen. Wir sind nicht verantwortlich für einen Missbrauch der Bibliothek.

Gemacht mit ❤️ von [ScrapeGraph AI](https://scrapegraphai.com)

[Scarf tracking](https://static.scarf.sh/a.png?x-pxid=102d4b8c-cd6a-4b9e-9a16-d6d141b9212d)
