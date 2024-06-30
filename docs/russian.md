# 🕷️ ScrapeGraphAI: Вы скрейпите только один раз

[![Downloads](https://img.shields.io/pepy/dt/scrapegraphai?style=for-the-badge)](https://pepy.tech/project/scrapegraphai)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen?style=for-the-badge)](https://github.com/pylint-dev/pylint)
[![Pylint](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/pylint.yml?label=Pylint&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/pylint.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/codeql.yml?label=CodeQL&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![](https://dcbadge.vercel.app/api/server/gkxQDAjfeX)](https://discord.gg/gkxQDAjfeX)

ScrapeGraphAI - это библиотека для веб-скрейпинга на Python, которая использует LLM и прямую графовую логику для создания скрейпинговых пайплайнов для веб-сайтов и локальных документов (XML, HTML, JSON и т.д.).

Просто укажите, какую информацию вы хотите извлечь, и библиотека сделает это за вас!

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapegraphai_logo.png" alt="Scrapegraph-ai Logo" style="width: 50%;">
</p>

## 🚀 Быстрая установка

Референсная страница для Scrapegraph-ai доступна на официальной странице PyPI: [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai
```

**Примечание**: рекомендуется устанавливать библиотеку в виртуальную среду, чтобы избежать конфликтов с другими библиотеками 🐱

## 🔍 Демонстрация

Официальная демонстрация на Streamlit:

[![My Skills](https://skillicons.dev/icons?i=react)](https://scrapegraph-ai-web-dashboard.streamlit.app)

Попробуйте ее прямо в интернете, используя Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

## 📖 Документация

Документация для ScrapeGraphAI доступна [здесь](https://scrapegraph-ai.readthedocs.io/en/latest/)..

Посмотрите также Docusaurus [здесь](https://scrapegraph-doc.onrender.com/).

## 💻 Использование

Существует три основных скрейпинговых пайплайна, которые можно использовать для извлечения информации с веб-сайта (или локального файла):

`SmartScraperGraph`: скрейпер одной страницы, которому требуется только пользовательский запрос и источник ввода;
`SearchGraph`: многопользовательский скрейпер, который извлекает информацию из топ n результатов поиска поисковой системы;
`SpeechGraph`: скрейпер одной страницы, который извлекает информацию с веб-сайта и генерирует аудиофайл.
`SmartScraperMultiGraph`: скрейпер нескольких страниц по одному запросу.

Можно использовать различные LLM через API, такие как **OpenAI**, **Groq**, **Azure** и **Gemini**, или локальные модели, используя **Ollama**.

### Пример 1: SmartScraper с использованием локальных моделей

Не забудьте установить [Ollama](https://ollama.com/) и загрузить модели, используя команду `ollama pull`.

```python
from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json",  # Ollama требует явного указания формата
        "base_url": "http://localhost:11434",  # укажите URL Ollama
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://localhost:11434",  # укажите URL Ollama
    },
    "verbose": True,
}

smart_scraper_graph = SmartScraperGraph(
    prompt="Перечислите все проекты с их описаниями",
    # также принимает строку с уже загруженным HTML-кодом
    source="https://perinim.github.io/projects",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
```

Выходные данные будут представлять собой список проектов с их описаниями, например:

```python
{'projects': [{'title': 'Rotary Pendulum RL', 'description': 'Open Source проект, направленный на управление реальным роторным маятником с использованием алгоритмов RL'}, {'title': 'DQN Implementation from scratch', 'description': 'Разработан алгоритм Deep Q-Network для обучения простого и двойного маятника'}, ...]}
```

### Пример 2: SearchGraph с использованием смешанных моделей

Мы используем **Groq** для LLM и **Ollama** для встраивания.

```python
from scrapegraphai.graphs import SearchGraph

# Определите конфигурацию для графа
graph_config = {
    "llm": {
        "model": "groq/gemma-7b-it",
        "api_key": "GROQ_API_KEY",
        "temperature": 0
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://localhost:11434",  # укажите URL Ollama произвольно
    },
    "max_results": 5,
}

# Создайте экземпляр SearchGraph
search_graph = SearchGraph(
    prompt="Перечислите все традиционные рецепты из Кьоджи",
    config=graph_config
)

# Запустите граф
result = search_graph.run()
print(result)
```

Выходные данные будут представлять собой список рецептов, например:

```python
{'recipes': [{'name': 'Sarde in Saòre'}, {'name': 'Bigoli in salsa'}, {'name': 'Seppie in umido'}, {'name': 'Moleche frite'}, {'name': 'Risotto alla pescatora'}, {'name': 'Broeto'}, {'name': 'Bibarasse in Cassopipa'}, {'name': 'Risi e bisi'}, {'name': 'Smegiassa Ciosota'}]}
```

### Пример 3: SpeechGraph с использованием OpenAI

Вам просто нужно передать ключ API OpenAI и название модели.

```python
from scrapegraphai.graphs import SpeechGraph

graph_config = {
    "llm": {
        "api_key": "OPENAI_API_KEY",
        "model": "gpt-3.5-turbo",
    },
    "tts_model": {
        "api_key": "OPENAI_API_KEY",
        "model": "tts-1",
        "voice": "alloy"
    },
    "output_path": "audio_summary.mp3",
}

# ************************************************
# Создайте экземпляр SpeechGraph и запустите его
# ************************************************

speech_graph = SpeechGraph(
    prompt="Сделайте подробное аудиорезюме проектов.",
    source="https://perinim.github.io/projects/",
    config=graph_config,
)

result = speech_graph.run()
print(result)
```

Выходные данные будут представлять собой аудиофайл с резюме проектов на странице.

## Спонсоры

<div style="text-align: center;">
  <a href="https://serpapi.com?utm_source=scrapegraphai">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/serp_api_logo.png" alt="SerpAPI" style="width: 10%;">
  </a>
  <a href="https://dashboard.statproxies.com/?refferal=scrapegraph">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/transparent_stat.png" alt="Stats" style="width: 15%;">
  </a>
</div>

## 🤝 Участие

Не стесняйтесь вносить свой вклад и присоединяйтесь к нашему серверу Discord, чтобы обсудить с нами улучшения и дать нам предложения!

Пожалуйста, ознакомьтесь с [руководством по участию](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/CONTRIBUTING.md).

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 📈 Дорожная карта

Посмотрите дорожную карту проекта [здесь](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/README.md)! 🚀

Хотите визуализировать дорожную карту более интерактивно? Посмотрите визуализацию [markmap](https://markmap.js.org/repl), скопировав содержимое markdown в редактор!

## ❤️ Разработчики программного обеспечения

[![Contributors](https://contrib.rocks/image?repo=VinciGit00/Scrapegraph-ai)](https://github.com/VinciGit00/Scrapegraph-ai/graphs/contributors)

## 🎓 Цитаты

Если вы использовали нашу библиотеку для научных исследований, пожалуйста, укажите нас в следующем виде:

```text
  @misc{scrapegraph-ai,
    author = {Марко Перини, Лоренцо Падоан, Марко Винчигуэрра},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/VinciGit00/Scrapegraph-ai},
    note = {Библиотека на Python для скрейпинга с использованием больших языковых моделей}
  }
```

## Авторы

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/logo_authors.png" alt="Authors_logos">
</p>

|                    | Контактная информация  |
|--------------------|------------------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/)    |
| Marco Perini       | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/perinim/)   |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)  |

## 📜 Лицензия

ScrapeGraphAI лицензирован под MIT License. Подробнее см. в файле [LICENSE](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/LICENSE).

## Благодарности

- Мы хотели бы поблагодарить всех участников проекта и сообщество с открытым исходным кодом за их поддержку.
- ScrapeGraphAI предназначен только для исследования данных и научных целей. Мы не несем ответственности за неправильное использование библиотеки.