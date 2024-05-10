
# 🕷️ ScrapeGraphAI: You Only Scrape Once
[![Downloads](https://static.pepy.tech/badge/scrapegraphai)](https://pepy.tech/project/scrapegraphai)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/pylint-dev/pylint)
[![Pylint](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/pylint.yml/badge.svg)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/pylint.yml)
[![CodeQL](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/codeql.yml/badge.svg)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![](https://dcbadge.vercel.app/api/server/gkxQDAjfeX)](https://discord.gg/gkxQDAjfeX)


ScrapeGraphAI is a *web scraping* python library that uses LLM and direct graph logic to create scraping pipelines for websites, documents and XML files.
Just say which information you want to extract and the library will do it for you!

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapegraphai_logo.png" alt="Scrapegraph-ai Logo" style="width: 50%;">
</p>

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/gkxQDAjfeX)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)


## 🚀 Quick install

The reference page for Scrapegraph-ai is available on the official page of pypy: [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai
```
you will also need to install Playwright for javascript-based scraping:
```bash
playwright install
```

**Note**: it is recommended to install the library in a virtual environment to avoid conflicts with other libraries 🐱

## 🔍 Demo
Official streamlit demo:

[![My Skills](https://skillicons.dev/icons?i=react)](https://scrapegraph-ai-demo.streamlit.app/)

Try it directly on the web using Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

Follow the procedure on the following link to setup your OpenAI API key: [link](https://scrapegraph-ai.readthedocs.io/en/latest/index.html).

## 📖 Documentation

The documentation for ScrapeGraphAI can be found [here](https://scrapegraph-ai.readthedocs.io/en/latest/).

Check out also the docusaurus [documentation](https://scrapegraph-doc.onrender.com/).

## 💻 Usage
You can use the `SmartScraper` class to extract information from a website using a prompt.

The `SmartScraper` class is a direct graph implementation that uses the most common nodes present in a web scraping pipeline. For more information, please see the [documentation](https://scrapegraph-ai.readthedocs.io/en/latest/).
### Case 1: Extracting information using Ollama
Remember to download the model on Ollama separately!

```python
from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
        "base_url": "http://localhost:11434",  # set Ollama URL
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://localhost:11434",  # set Ollama URL
    }
}

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the articles",
    # also accepts a string with the already downloaded HTML code
    source="https://perinim.github.io/projects",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)

```

### Case 2: Extracting information using Docker

Note: before using the local model remember to create the docker container!
```text
    docker-compose up -d
    docker exec -it ollama ollama pull stablelm-zephyr
```
You can use which models available on Ollama or your own model instead of stablelm-zephyr
```python
from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json",  # Ollama needs the format to be specified explicitly
        # "model_tokens": 2000, # set context length arbitrarily
    },
}

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the articles",
    # also accepts a string with the already downloaded HTML code
    source="https://perinim.github.io/projects",  
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
```


### Case 3: Extracting information using Openai model
```python
from scrapegraphai.graphs import SmartScraperGraph
OPENAI_API_KEY = "YOUR_API_KEY"

graph_config = {
    "llm": {
        "api_key": OPENAI_API_KEY,
        "model": "gpt-3.5-turbo",
    },
}

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the articles",
    # also accepts a string with the already downloaded HTML code
    source="https://perinim.github.io/projects",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
```

### Case 4: Extracting information using Groq
```python
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info

groq_key = os.getenv("GROQ_APIKEY")

graph_config = {
    "llm": {
        "model": "groq/gemma-7b-it",
        "api_key": groq_key,
        "temperature": 0
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "temperature": 0,
        "base_url": "http://localhost:11434", 
    },
    "headless": False
}

smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the projects with their description and the author.",
    source="https://perinim.github.io/projects",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
```

### Case 5: Extracting information using Azure
```python
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings

lm_model_instance = AzureChatOpenAI(
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    azure_deployment=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

embedder_model_instance = AzureOpenAIEmbeddings(
    azure_deployment=os.environ["AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME"],
    openai_api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)
graph_config = {
    "llm": {"model_instance": llm_model_instance},
    "embeddings": {"model_instance": embedder_model_instance}
}

smart_scraper_graph = SmartScraperGraph(
    prompt="""List me all the events, with the following fields: company_name, event_name, event_start_date, event_start_time, 
    event_end_date, event_end_time, location, event_mode, event_category, 
    third_party_redirect, no_of_days, 
    time_in_hours, hosted_or_attending, refreshments_type, 
    registration_available, registration_link""",
    source="https://www.hmhco.com/event",
    config=graph_config
)
```

### Case 6: Extracting information using Gemini 
```python
from scrapegraphai.graphs import SmartScraperGraph
GOOGLE_APIKEY = "YOUR_API_KEY"

# Define the configuration for the graph
graph_config = {
    "llm": {
        "api_key": GOOGLE_APIKEY,
        "model": "gemini-pro",
    },
}

# Create the SmartScraperGraph instance
smart_scraper_graph = SmartScraperGraph(
    prompt="List me all the articles",
    source="https://perinim.github.io/projects",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
```

The output for all 3 the cases will be a dictionary with the extracted information, for example:

```bash
{
    'titles': [
        'Rotary Pendulum RL'
        ],
    'descriptions': [
        'Open Source project aimed at controlling a real life rotary pendulum using RL algorithms'
        ]
}
```

## 🤝 Contributing

Feel free to contribute and join our Discord server to discuss with us improvements and give us suggestions!

Please see the [contributing guidelines](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/CONTRIBUTING.md).

## 📈 Roadmap
Check out the project roadmap [here](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/README.md)! 🚀

Wanna visualize the roadmap in a more interactive way? Check out the [markmap](https://markmap.js.org/repl) visualization by copy pasting the markdown content in the editor!

## ❤️ Contributors
[![Contributors](https://contrib.rocks/image?repo=VinciGit00/Scrapegraph-ai)](https://github.com/VinciGit00/Scrapegraph-ai/graphs/contributors)
## Sponsors
<p align="center">
  <a href="https://serpapi.com/"><img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/serp_api_logo.png" alt="SerpAPI" style="width: 10%;"></a>
</p>

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
