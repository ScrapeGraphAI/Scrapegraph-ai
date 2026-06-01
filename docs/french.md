## 🚀 **Vous cherchez un moyen encore plus rapide et plus simple de scraper à grande échelle (seulement 5 lignes de code) ?** Découvrez notre version améliorée sur [**ScrapeGraphAI.com**](https://scrapegraphai.com/?utm_source=github&utm_medium=readme&utm_campaign=oss_cta&utm_content=top_banner) ! 🚀

---

# 🕷️ ScrapeGraphAI: Vous ne scrapez qu'une fois

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

[ScrapeGraphAI](https://scrapegraphai.com) est une bibliothèque Python de *web scraping* qui utilise les LLM et la logique de graphes directs pour créer des pipelines de scraping pour les sites web et les documents locaux (XML, HTML, JSON, Markdown, etc.).

Dites simplement quelles informations vous souhaitez extraire et la bibliothèque le fera pour vous !

<p align="center">
  <img src="https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/sgai-hero.png" alt="ScrapeGraphAI Hero" style="width: 100%;">
</p>

## 🚀 Intégrations

ScrapeGraphAI offre une intégration transparente avec les frameworks et outils populaires pour améliorer vos capacités de scraping. Que vous développiez avec Python ou Node.js, utilisiez des frameworks LLM ou travailliez avec des plateformes no-code, nous avons tout prévu avec nos options d'intégration complètes.

Vous pouvez trouver plus d'informations sur le [lien](https://scrapegraphai.com) suivant.

**Intégrations**:
- **API**: [Documentation](https://docs.scrapegraphai.com/introduction)
- **SDKs**: [Python](https://docs.scrapegraphai.com/sdks/python), [Node](https://docs.scrapegraphai.com/sdks/javascript)
- **Frameworks LLM**: [Langchain](https://docs.scrapegraphai.com/integrations/langchain), [Llama Index](https://docs.scrapegraphai.com/integrations/llamaindex), [Crew.ai](https://docs.scrapegraphai.com/integrations/crewai), [Agno](https://docs.scrapegraphai.com/integrations/agno), [CamelAI](https://github.com/camel-ai/camel)
- **Frameworks Low-code**: [Pipedream](https://pipedream.com/apps/scrapegraphai), [Bubble](https://bubble.io/plugin/scrapegraphai-1745408893195x213542371433906180), [Zapier](https://zapier.com/apps/scrapegraphai/integrations), [n8n](http://localhost:5001/dashboard), [Dify](https://dify.ai), [Toolhouse](https://app.toolhouse.ai/mcp-servers/scrapegraph_smartscraper)
- **Serveur MCP**:  [Lien](https://smithery.ai/server/@ScrapeGraphAI/scrapegraph-mcp)

## 🚀 Installation rapide

La page de référence pour Scrapegraph-ai est disponible sur la page officielle de PyPI : [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai

# IMPORTANT (pour récupérer le contenu des sites web)
playwright install
```

**Remarque** : il est recommandé d'installer la bibliothèque dans un environnement virtuel pour éviter les conflits avec d'autres bibliothèques 🐱

## 💻 Utilisation
Il existe plusieurs pipelines de scraping standards qui peuvent être utilisés pour extraire des informations d'un site web (ou d'un fichier local).

Le plus courant est le `SmartScraperGraph`, qui extrait les informations d'une seule page à partir d'une invite utilisateur et d'une URL source.

```python
from scrapegraphai.graphs import SmartScraperGraph

# Définir la configuration pour le pipeline de scraping
graph_config = {
    "llm": {
        "model": "ollama/llama3.2",
        "model_tokens": 8192,
        "format": "json",
    },
    "verbose": True,
    "headless": False,
}

# Créer l'instance SmartScraperGraph
smart_scraper_graph = SmartScraperGraph(
    prompt="Extract useful information from the webpage, including a description of what the company does, founders and social media links",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# Exécuter le pipeline
result = smart_scraper_graph.run()

import json
print(json.dumps(result, indent=4))
```

> [!NOTE]
> Pour OpenAI et d'autres modèles, il vous suffit de modifier la configuration LLM !
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

La sortie sera un dictionnaire comme suit :

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
Il existe d'autres pipelines qui peuvent être utilisés pour extraire des informations de plusieurs pages, générer des scripts Python, ou même générer des fichiers audio.

| Nom du pipeline         | Description                                                                                                      |
|-------------------------|------------------------------------------------------------------------------------------------------------------|
| SmartScraperGraph       | Scraper d'une seule page qui n'a besoin que d'une invite utilisateur et d'une source d'entrée.                  |
| SearchGraph             | Scraper multi-pages qui extrait des informations des n premiers résultats d'un moteur de recherche.              |
| SpeechGraph             | Scraper d'une seule page qui extrait des informations d'un site web et génère un fichier audio.                  |
| ScriptCreatorGraph      | Scraper d'une seule page qui extrait des informations d'un site web et génère un script Python.                  |
| SmartScraperMultiGraph  | Scraper multi-pages qui extrait des informations de plusieurs pages à partir d'une seule invite et d'une liste de sources.    |
| ScriptCreatorMultiGraph | Scraper multi-pages qui génère un script Python pour extraire des informations de plusieurs pages et sources.    |

Pour chacun de ces graphes, il existe la version multi. Elle permet de faire des appels au LLM en parallèle.

Il est possible d'utiliser différents LLM via des API, telles qu'**OpenAI**, **Groq**, **Azure**, **Gemini**, **MiniMax** et d'autres, ou des modèles locaux en utilisant **Ollama**.

N'oubliez pas d'installer [Ollama](https://ollama.com/) et de télécharger les modèles en utilisant la commande **ollama pull**, si vous souhaitez utiliser des modèles locaux.

## 📖 Documentation

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

La documentation pour ScrapeGraphAI se trouve [ici](https://docs.scrapegraphai.com/introduction).

## 🤝 Contribuer

N'hésitez pas à contribuer et à rejoindre notre serveur Discord pour discuter avec nous des améliorations et nous donner des suggestions !

Veuillez consulter les [directives de contribution](https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/CONTRIBUTING.md).

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 🔗 API et SDK ScrapeGraph
Si vous cherchez une solution rapide pour intégrer ScrapeGraph dans votre système, consultez notre puissante API [ici !](https://dashboard.scrapegraphai.com/login)

[![API Banner](https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/api_banner.png)](https://dashboard.scrapegraphai.com/login)

Nous proposons des SDK en Python et Node.js, ce qui facilite leur intégration dans vos projets. Découvrez-les ci-dessous :

| SDK       | Langage  | Lien GitHub                                                                 |
|-----------|----------|-----------------------------------------------------------------------------|
| Python SDK | Python   | [scrapegraph-py](https://docs.scrapegraphai.com/sdks/python) |
| Node.js SDK | Node.js  | [scrapegraph-js](https://docs.scrapegraphai.com/sdks/javascript) |

La documentation officielle de l'API est disponible [ici](https://docs.scrapegraphai.com/introduction).

## 🔥 Benchmark

Selon le benchmark Firecrawl [Firecrawl benchmark](https://scrapegraphai.com/compare/firecrawl), ScrapeGraph est le meilleur scraper sur le marché !

![here](assets/histogram.png)

## 📈 Télémétrie
Nous recueillons des mesures d'utilisation anonymes pour améliorer la qualité de notre package et l'expérience utilisateur. Les données nous aident à hiérarchiser les améliorations et à assurer la compatibilité. Si vous souhaitez vous désinscrire, définissez la variable d'environnement SCRAPEGRAPHAI_TELEMETRY_ENABLED=false. Pour plus d'informations, veuillez consulter la documentation [ici](https://docs.scrapegraphai.com/introduction).

## ❤️ Contributeurs
[![Contributors](https://contrib.rocks/image?repo=ScrapeGraphAI/Scrapegraph-ai)](https://github.com/ScrapeGraphAI/Scrapegraph-ai/graphs/contributors)

## 🎓 Citations
Si vous avez utilisé notre bibliothèque à des fins de recherche, veuillez nous citer avec la référence suivante :
```text
  @misc{scrapegraph-ai,
    author = {Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/ScrapeGraphAI/Scrapegraph-ai},
    note = {A Python library for scraping leveraging large language models}
  }
```
## Auteurs

|                    | Info Contact         |
|--------------------|----------------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/)    |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)  |

## 📜 Licence

ScrapeGraphAI est sous licence MIT. Consultez le fichier [LICENSE](https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/LICENSE) pour plus d'informations.

## Remerciements

- Nous tenons à remercier tous les contributeurs au projet et la communauté open-source pour leur soutien.
- ScrapeGraphAI est destiné uniquement à l'exploration de données et à la recherche. Nous ne sommes pas responsables de toute mauvaise utilisation de la bibliothèque.

Fait avec ❤️ par [ScrapeGraph AI](https://scrapegraphai.com)

[Scarf tracking](https://static.scarf.sh/a.png?x-pxid=102d4b8c-cd6a-4b9e-9a16-d6d141b9212d)
