## 🚀 **¿Buscas una forma aún más rápida y sencilla de hacer scraping a escala (con solo 5 líneas de código)?** ¡Checa nuestra versión mejorada en [**ScrapeGraphAI.com**](https://scrapegraphai.com/?utm_source=github&utm_medium=readme&utm_campaign=oss_cta&utm_content=top_banner)! 🚀

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

[ScrapeGraphAI](https://scrapegraphai.com) es una librería de Python para *web scraping* que usa LLMs y lógica de grafos para crear pipelines de extracción de datos en sitios web y documentos locales (XML, HTML, JSON, Markdown, etc.).

¡Solo dile qué información quieres extraer y la librería lo hace por ti!

<p align="center">
  <img src="https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/sgai-hero.png" alt="ScrapeGraphAI Hero" style="width: 100%;">
</p>

## 🚀 Integraciones

ScrapeGraphAI se integra de forma nativa con los frameworks y herramientas más populares para potenciar tus capacidades de scraping. Ya sea que estés desarrollando en Python o Node.js, usando frameworks de LLMs o plataformas no-code, tenemos todo cubierto.

Puedes encontrar más información en el siguiente [link](https://scrapegraphai.com)

**Integraciones**:
- **API**: [Documentación](https://docs.scrapegraphai.com/introduction)
- **SDKs**: [Python](https://docs.scrapegraphai.com/sdks/python), [Node](https://docs.scrapegraphai.com/sdks/javascript)
- **Frameworks de LLMs**: [Langchain](https://docs.scrapegraphai.com/integrations/langchain), [Llama Index](https://docs.scrapegraphai.com/integrations/llamaindex), [Crew.ai](https://docs.scrapegraphai.com/integrations/crewai), [Agno](https://docs.scrapegraphai.com/integrations/agno), [CamelAI](https://github.com/camel-ai/camel)
- **Frameworks low-code**: [Pipedream](https://pipedream.com/apps/scrapegraphai), [Bubble](https://bubble.io/plugin/scrapegraphai-1745408893195x213542371433906180), [Zapier](https://zapier.com/apps/scrapegraphai/integrations), [n8n](http://localhost:5001/dashboard), [Dify](https://dify.ai), [Toolhouse](https://app.toolhouse.ai/mcp-servers/scrapegraph_smartscraper)
- **Servidor MCP**: [Link](https://smithery.ai/server/@ScrapeGraphAI/scrapegraph-mcp)

## 🚀 Instalación rápida

La página de referencia de Scrapegraph-ai está disponible en PyPI: [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai

# IMPORTANTE (para hacer fetch del contenido de los sitios web)
playwright install
```

**Nota**: se recomienda instalar la librería en un entorno virtual para evitar conflictos con otras dependencias 🐱


## 💻 Uso

Hay múltiples pipelines de scraping estándar para extraer información de un sitio web o archivo local.

El más común es `SmartScraperGraph`, que extrae información de una sola página dado un prompt y una URL de origen.

```python
from scrapegraphai.graphs import SmartScraperGraph

# Define the configuration for the scraping pipeline
graph_config = {
    "llm": {
        "model": "ollama/llama3.2",
        "model_tokens": 8192,
        "format": "json",
    },
    "verbose": True,
    "headless": False,
}

# Create the SmartScraperGraph instance
smart_scraper_graph = SmartScraperGraph(
    prompt="Extract useful information from the webpage, including a description of what the company does, founders and social media links",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# Run the pipeline
result = smart_scraper_graph.run()

import json
print(json.dumps(result, indent=4))
```

> [!NOTE]
> Para OpenAI y otros modelos solo necesitas cambiar el config del LLM:
> ```python
> graph_config = {
>     "llm": {
>         "api_key": "YOUR_OPENAI_API_KEY",
>         "model": "openai/gpt-4o-mini",
>     },
>     "verbose": True,
>     "headless": False,
> }
> ```


El output será un diccionario como el siguiente:

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

Existen otros pipelines para extraer información de múltiples páginas, generar scripts de Python o incluso generar archivos de audio.

| Nombre del Pipeline     | Descripción                                                                                                           |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------|
| SmartScraperGraph       | Scraper de una sola página que solo requiere un prompt y una fuente de entrada.                                       |
| SearchGraph             | Scraper multi-página que extrae información de los primeros n resultados de un motor de búsqueda.                     |
| SpeechGraph             | Scraper de una sola página que extrae información de un sitio web y genera un archivo de audio.                       |
| ScriptCreatorGraph      | Scraper de una sola página que extrae información de un sitio web y genera un script de Python.                       |
| SmartScraperMultiGraph  | Scraper multi-página que extrae información de múltiples páginas con un solo prompt y una lista de fuentes.           |
| ScriptCreatorMultiGraph | Scraper multi-página que genera un script de Python para extraer información de múltiples páginas y fuentes.           |

Cada uno de estos grafos tiene su versión multi, que permite hacer llamadas al LLM en paralelo.

Es posible usar diferentes LLMs mediante APIs como **OpenAI**, **Groq**, **Azure**, **Gemini**, **MiniMax** y más, o modelos locales usando **Ollama**.

Recuerda tener [Ollama](https://ollama.com/) instalado y descargar los modelos con el comando **ollama pull** si quieres usar modelos locales.


## 📖 Documentación

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

La documentación de ScrapeGraphAI está disponible [aquí](https://docs.scrapegraphai.com/introduction).

## 🤝 Contribuciones

¡Siéntete libre de contribuir y únete a nuestro servidor de Discord para discutir mejoras y compartir sugerencias!

Por favor revisa las [guías de contribución](https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/CONTRIBUTING.md).

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 🔗 API y SDKs de ScrapeGraph

Si buscas una solución rápida para integrar ScrapeGraph en tu sistema, checa nuestra API [aquí](https://dashboard.scrapegraphai.com/login).

[![API Banner](https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/api_banner.png)](https://dashboard.scrapegraphai.com/login)

Ofrecemos SDKs en Python y Node.js para facilitar la integración en tus proyectos:

| SDK         | Lenguaje | GitHub Link                                                                                  |
|-------------|----------|----------------------------------------------------------------------------------------------|
| Python SDK  | Python   | [scrapegraph-py](https://docs.scrapegraphai.com/sdks/python) |
| Node.js SDK | Node.js  | [scrapegraph-js](https://docs.scrapegraphai.com/sdks/javascript) |

La documentación oficial de la API está disponible [aquí](https://docs.scrapegraphai.com/introduction).

## 🔥 Benchmark

¡Según el benchmark de Firecrawl [Firecrawl benchmark](https://scrapegraphai.com/compare/firecrawl), ScrapeGraph es el mejor fetcher del mercado!

![here](assets/histogram.png)

## 📈 Telemetría

Recopilamos métricas de uso anónimas para mejorar la calidad del paquete y la experiencia del usuario. Los datos nos ayudan a priorizar mejoras y garantizar compatibilidad. Si deseas hacer opt-out, configura la variable de entorno `SCRAPEGRAPHAI_TELEMETRY_ENABLED=false`. Para más información consulta la documentación [aquí](https://docs.scrapegraphai.com/introduction).

## ❤️ Contributors

[![Contributors](https://contrib.rocks/image?repo=ScrapeGraphAI/Scrapegraph-ai)](https://github.com/ScrapeGraphAI/Scrapegraph-ai/graphs/contributors)

## 🎓 Citas

Si usaste nuestra librería para investigación, por favor cítanos con la siguiente referencia:

```text
  @misc{scrapegraph-ai,
    author = {Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/ScrapeGraphAI/Scrapegraph-ai},
    note = {A Python library for scraping leveraging large language models}
  }
```

## Autores

|                    | Contacto             |
|--------------------|----------------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/) |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)   |

## 📜 Licencia

ScrapeGraphAI está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](https://github.com/ScrapeGraphAI/Scrapegraph-ai/blob/main/LICENSE) para más información.

## Agradecimientos

- Queremos agradecer a todos los contributors del proyecto y a la comunidad open-source por su apoyo.
- ScrapeGraphAI está pensado únicamente para exploración de datos e investigación. No nos hacemos responsables del mal uso de la librería.

Hecho con ❤️ por [ScrapeGraph AI](https://scrapegraphai.com)

[Scarf tracking](https://static.scarf.sh/a.png?x-pxid=102d4b8c-cd6a-4b9e-9a16-d6d141b9212d)
