
# 🕷️ ScrapeGraphAI: You Only Scrape Once
[English](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/README.md) | [中文](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/chinese.md) | [日本語](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/japanese.md)
| [한국어](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/korean.md)
| [Русский](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/russian.md) | [Türkçe](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/turkish.md)


[![Downloads](https://img.shields.io/pepy/dt/scrapegraphai?style=for-the-badge)](https://pepy.tech/project/scrapegraphai)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen?style=for-the-badge)](https://github.com/pylint-dev/pylint)
[![Pylint](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/pylint.yml?label=Pylint&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/pylint.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/codeql.yml?label=CodeQL&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![](https://dcbadge.vercel.app/api/server/gkxQDAjfeX)](https://discord.gg/gkxQDAjfeX)

ScrapeGraphAI is a *web scraping* python library that uses LLM and direct graph logic to create scraping pipelines for websites and local documents (XML, HTML, JSON, Markdown, etc.).

Just say which information you want to extract and the library will do it for you!

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/sgai-hero.png" alt="ScrapeGraphAI Hero" style="width: 100%;">
</p>

## 🚀 Quick install

The reference page for Scrapegraph-ai is available on the official page of PyPI: [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai

playwright install
```

**Note**: it is recommended to install the library in a virtual environment to avoid conflicts with other libraries 🐱

<details>
<summary><b>Optional Dependencies</b></summary>
Additional dependecies can be added while installing the library:

- <b>More Language Models</b>: additional language models are installed, such as Fireworks, Groq, Anthropic, Hugging Face, and Nvidia AI Endpoints.

  This group allows you to use additional language models like Fireworks, Groq, Anthropic, Together AI, Hugging Face, and Nvidia AI Endpoints.
  ```bash
  pip install scrapegraphai[other-language-models]
  ```
- <b>Semantic Options</b>: this group includes tools for advanced semantic processing, such as Graphviz.

  ```bash
  pip install scrapegraphai[more-semantic-options]
  ```

- <b>Browsers Options</b>: this group includes additional browser management tools/services, such as Browserbase.

  ```bash
  pip install scrapegraphai[more-browser-options]
  ```

</details>


## 💻 Usage
There are multiple standard scraping pipelines that can be used to extract information from a website (or local file).

The most common one is the `SmartScraperGraph`, which extracts information from a single page given a user prompt and a source URL.


```python
import json
from scrapegraphai.graphs import SmartScraperGraph

# Define the configuration for the scraping pipeline
graph_config = {
    "llm": {
        "api_key": "YOUR_OPENAI_APIKEY",
        "model": "openai/gpt-4o-mini",
    },
    "verbose": True,
    "headless": False,
}

# Create the SmartScraperGraph instance
smart_scraper_graph = SmartScraperGraph(
    prompt="Find some information about what does the company do, the name and a contact email.",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# Run the pipeline
result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))
```

The output will be a dictionary like the following:

```python
{
    "company": "ScrapeGraphAI",
    "name": "ScrapeGraphAI Extracting content from websites and local documents using LLM",
    "contact_email": "contact@scrapegraphai.com"
}
```
There are other pipelines that can be used to extract information from multiple pages, generate Python scripts, or even generate audio files.

| Pipeline Name           | Description                                                                                                      |
|-------------------------|------------------------------------------------------------------------------------------------------------------|
| SmartScraperGraph       | Single-page scraper that only needs a user prompt and an input source.                                           |
| SearchGraph             | Multi-page scraper that extracts information from the top n search results of a search engine.                  |
| SpeechGraph             | Single-page scraper that extracts information from a website and generates an audio file.                       |
| ScriptCreatorGraph      | Single-page scraper that extracts information from a website and generates a Python script.                     |
| SmartScraperMultiGraph  | Multi-page scraper that extracts information from multiple pages given a single prompt and a list of sources.    |
| ScriptCreatorMultiGraph | Multi-page scraper that generates a Python script for extracting information from multiple pages and sources.     |

For each of these graphs there is the multi version. It allows to make calls of the LLM in parallel.

It is possible to use different LLM through APIs, such as **OpenAI**, **Groq**, **Azure** and **Gemini**, or local models using **Ollama**.

Remember to have [Ollama](https://ollama.com/) installed and download the models using the **ollama pull** command, if you want to use local models.

## 🔍 Demo
Official streamlit demo:

[![My Skills](https://skillicons.dev/icons?i=react)](https://scrapegraph-ai-web-dashboard.streamlit.app)

Try it directly on the web using Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

## 📖 Documentation

The documentation for ScrapeGraphAI can be found [here](https://scrapegraph-ai.readthedocs.io/en/latest/).

Check out also the Docusaurus [here](https://scrapegraph-doc.onrender.com/).

## 🏆 Sponsors
<div style="text-align: center;">
  <a href="https://2ly.link/1zaXG">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/browserbase_logo.png" alt="Browserbase" style="width: 10%;">
  </a>
  <a href="https://2ly.link/1zNiz">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/serp_api_logo.png" alt="SerpAPI" style="width: 10%;">
  </a>
  <a href="https://2ly.link/1zNj1">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/transparent_stat.png" alt="Stats" style="width: 15%;">
  </a>
    <a href="https://scrape.do">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapedo.png" alt="Stats" style="width: 11%;">
  </a>
</div>

## 🤝 Contributing

Feel free to contribute and join our Discord server to discuss with us improvements and give us suggestions!

Please see the [contributing guidelines](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/CONTRIBUTING.md).

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 📈 Telemetry 
We collect anonymous usage metrics to enhance our package's quality and user experience. The data helps us prioritize improvements and ensure compatibility. If you wish to opt-out, set the environment variable SCRAPEGRAPHAI_TELEMETRY_ENABLED=false. For more information, please refer to the documentation [here](https://scrapegraph-ai.readthedocs.io/en/latest/scrapers/telemetry.html).


## ❤️ Contributors
[![Contributors](https://contrib.rocks/image?repo=VinciGit00/Scrapegraph-ai)](https://github.com/VinciGit00/Scrapegraph-ai/graphs/contributors)

## 🎓 Citations
If you have used our library for research purposes please quote us with the following reference:
```text
  @misc{scrapegraph-ai,
    author = {Marco Perini, Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/VinciGit00/Scrapegraph-ai},
    note = {A Python library for scraping leveraging large language models}
  }
```

## Authors

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/logo_authors.png" alt="Authors_logos">
</p>

|                    | Contact Info         |
|--------------------|----------------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/)    |
| Marco Perini       | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/perinim/)   |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)  |

## 📜 License

ScrapeGraphAI is licensed under the MIT License. See the [LICENSE](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/LICENSE) file for more information.

## Acknowledgements

- We would like to thank all the contributors to the project and the open-source community for their support.
- ScrapeGraphAI is meant to be used for data exploration and research purposes only. We are not responsible for any misuse of the library.
