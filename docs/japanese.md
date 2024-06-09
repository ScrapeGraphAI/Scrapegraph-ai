# 🕷️ ScrapeGraphAI: 一度のクロールで完結
[![Downloads](https://img.shields.io/pepy/dt/scrapegraphai?style=for-the-badge)](https://pepy.tech/project/scrapegraphai)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen?style=for-the-badge)](https://github.com/pylint-dev/pylint)
[![Pylint](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/pylint.yml?style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/pylint.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/codeql.yml?style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![](https://dcbadge.vercel.app/api/server/gkxQDAjfeX)](https://discord.gg/gkxQDAjfeX)

ScrapeGraphAIは、大規模言語モデルと直接グラフロジックを使用して、ウェブサイトやローカルドキュメント（XML、HTML、JSONなど）のクローリングパイプラインを作成するPythonライブラリです。

クロールしたい情報をライブラリに伝えるだけで、残りはすべてライブラリが行います！

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapegraphai_logo.png" alt="Scrapegraph-ai Logo" style="width: 50%;">
</p>

## 🚀 インストール方法

Scrapegraph-aiの参照ページはPyPIの公式サイトで見ることができます: [pypi](https://pypi.org/project/scrapegraphai/)。

```bash
pip install scrapegraphai
```
**注意**: 他のライブラリとの競合を避けるため、このライブラリは仮想環境でのインストールを推奨します 🐱

## 🔍 デモ

公式のStreamlitデモ：

[![My Skills](https://skillicons.dev/icons?i=react)](https://scrapegraph-ai-web-dashboard.streamlit.app)

Google Colabで直接試す：

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

## 📖 ドキュメント

ScrapeGraphAIのドキュメントは[こちら](https://scrapegraph-ai.readthedocs.io/en/latest/)で見ることができます。

Docusaurusの[バージョン](https://scrapegraph-doc.onrender.com/)もご覧ください。

## 💻 使い方

ウェブサイト（またはローカルファイル）から情報を抽出するための3つの主要なクローリングパイプラインがあります：

- `SmartScraperGraph`: 単一ページのクローラー。ユーザープロンプトと入力ソースのみが必要です。
- `SearchGraph`: 複数ページのクローラー。検索エンジンの上位n個の検索結果から情報を抽出します。
- `SpeechGraph`: 単一ページのクローラー。ウェブサイトから情報を抽出し、音声ファイルを生成します。
- `SmartScraperMultiGraph`: 複数ページのクローラー。プロンプトを与えると、
**OpenAI**、**Groq**、**Azure**、**Gemini**などの異なるLLMをAPI経由で使用することができます。また、**Ollama**のローカルモデルを使用することもできます。

### 例 1: ローカルモデルを使用したSmartScraper
[Ollama](https://ollama.com/)がインストールされていること、および`ollama pull`コマンドでモデルがダウンロードされていることを確認してください。

``` python
from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json",  # Ollamaではフォーマットを明示的に指定する必要があります
        "base_url": "http://localhost:11434",  # OllamaのURLを設定
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://localhost:11434",  # OllamaのURLを設定
    },
    "verbose": True,
}

smart_scraper_graph = SmartScraperGraph(
    prompt="すべてのプロジェクトとその説明をリストしてください",
    # ダウンロード済みのHTMLコードの文字列も受け付けます
    source="https://perinim.github.io/projects",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
```

出力は、プロジェクトとその説明のリストになります：

```python
{'projects': [{'title': 'Rotary Pendulum RL', 'description': 'Open Source project aimed at controlling a real life rotary pendulum using RL algorithms'}, {'title': 'DQN Implementation from scratch', 'description': 'Developed a Deep Q-Network algorithm to train a simple and double pendulum'}, ...]}
```

### 例 2: 混合モデルを使用したSearchGraph
**Groq**をLLMとして、**Ollama**を埋め込みモデルとして使用します。

```python
from scrapegraphai.graphs import SearchGraph

# グラフの設定を定義
graph_config = {
    "llm": {
        "model": "groq/gemma-7b-it",
        "api_key": "GROQ_API_KEY",
        "temperature": 0
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://localhost:11434",  # OllamaのURLを任意に設定
    },
    "max_results": 5,
}

# SearchGraphインスタンスを作成
search_graph = SearchGraph(
    prompt="Chioggiaの伝統的なレシピをすべてリストしてください",
    config=graph_config
)

# グラフを実行
result = search_graph.run()
print(result)
```

出力は、レシピのリストになります：

```python
{'recipes': [{'name': 'Sarde in Saòre'}, {'name': 'Bigoli in salsa'}, {'name': 'Seppie in umido'}, {'name': 'Moleche frite'}, {'name': 'Risotto alla pescatora'}, {'name': 'Broeto'}, {'name': 'Bibarasse in Cassopipa'}, {'name': 'Risi e bisi'}, {'name': 'Smegiassa Ciosota'}]}
```

### 例 3: OpenAIを使用したSpeechGraph

OpenAI APIキーとモデル名を渡すだけです。

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
# SpeechGraphインスタンスを作成して実行
# ************************************************

speech_graph = SpeechGraph(
    prompt="プロジェクトの詳細な音声要約を作成してください。",
    source="https://perinim.github.io/projects/",
    config=graph_config,
)

result = speech_graph.run()
print(result)
```
出力は、ページ上のプロジェクトの要約を含む音声ファイルになります。

## スポンサー

<div style="text-align: center;">
  <a href="https://serpapi.com?utm_source=scrapegraphai">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/serp_api_logo.png" alt="SerpAPI" style="width: 10%;">
  </a>
  <a href="https://dashboard.statproxies.com/?refferal=scrapegraph">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/transparent_stat.png" alt="Stats" style="width: 15%;">
  </a>
</div>

## 🤝 貢献

貢献を歓迎し、Discordサーバーで改善や提案について話し合います！

[貢献ガイド](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/CONTRIBUTING.md)をご覧ください。

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)


## 📈 ロードマップ

[こちら](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/README.md)でプロジェクトのロードマップをご覧ください！ 🚀

よりインタラクティブな方法でロードマップを視覚化したいですか？[markmap](https://markmap.js.org/repl)をチェックして、マークダウンの内容をエディタにコピー＆ペーストして視覚化してください！

## ❤️ 貢献者
[![Contributors](https://contrib.rocks/image?repo=VinciGit00/Scrapegraph-ai)](https://github.com/VinciGit00/Scrapegraph-ai/graphs/contributors)


## 🎓 引用

研究目的で当社のライブラリを使用する場合は、以下の参考文献を引用してください：
```text
  @misc{scrapegraph-ai,
    author = {Marco Perini, Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/VinciGit00/Scrapegraph-ai},
    note = {A Python library for scraping leveraging large language models}
  }
```
## 作者

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/logo_authors.png" alt="Authors_logos">
</p>

## 連絡先
|                    | 連絡先         |
|--------------------|----------------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/)    |
| Marco Perini       | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/perinim/)   |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)  |

## 📜 ライセンス

ScrapeGraphAIはMITライセンスの下で提供されています。詳細は[LICENSE](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/LICENSE)ファイルをご覧ください。

## 謝辞

- プロジェクトの貢献者とオープンソースコミュニティのサポートに感謝します。
- ScrapeGraphAIはデータ探索と研究目的のみに使用されます。このライブラリの不正使用については一切責任を負いません。
