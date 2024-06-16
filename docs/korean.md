# 🕷️ ScrapeGraphAI: 한 번만 스크래핑하세요


ScrapeGraphAI는 웹 사이트와 로컬 문서(XML, HTML, JSON 등)에 대한 스크래핑 파이프라인을 만들기 위해 LLM 및 직접 그래프 로직을 사용하는 파이썬 웹 스크래핑 라이브러리입니다.

추출하려는 정보를 말하기만 하면 라이브러리가 알아서 처리해 줍니다!

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/scrapegraphai_logo.png" alt="Scrapegraph-ai Logo" style="width: 50%;">
</p>

## 🚀 빠른 설치

Scrapegraph-ai에 대한 참조 페이지는 PyPI의 공식 페이지에서 확인할 수 있습니다: pypi.

bash
Copia codice
pip install scrapegraphai
참고: 다른 라이브러리와의 충돌을 피하기 위해 라이브러리를 가상 환경에 설치하는 것이 좋습니다 🐱

## 🔍 데모

공식 Streamlit 데모:



Google Colab을 사용하여 웹에서 직접 사용해 보세요:



## 📖 문서

ScrapeGraphAI에 대한 문서는 여기에서 찾을 수 있습니다.

또한 Docusaurus를 여기에서 확인해 보세요.

## 💻 사용법

웹 사이트(또는 로컬 파일)에서 정보를 추출하는 데 사용할 수 있는 세 가지 주요 스크래핑 파이프라인이 있습니다:

SmartScraperGraph: 사용자 프롬프트와 입력 소스만 필요한 단일 페이지 스크래퍼;
SearchGraph: 검색 엔진의 상위 n개의 검색 결과에서 정보를 추출하는 다중 페이지 스크래퍼;
SpeechGraph: 웹 사이트에서 정보를 추출하고 오디오 파일을 생성하는 단일 페이지 스크래퍼.
SmartScraperMultiGraph: 단일 프롬프트를 사용하여 여러 페이지를 스크래핑하는 스크래퍼
OpenAI, Groq, Azure, Gemini와 같은 API를 통해 다양한 LLM을 사용할 수 있으며, Ollama를 사용하여 로컬 모델을 사용할 수도 있습니다.

사례 1: 로컬 모델을 사용하는 SmartScraper
Ollama를 설치하고 ollama pull 명령을 사용하여 모델을 다운로드하세요.

```python
from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 0,
        "format": "json",  # Ollama는 형식을 명시적으로 지정해야 합니다
        "base_url": "http://localhost:11434",  # Ollama URL 설정
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://localhost:11434",  # Ollama URL 설정
    },
    "verbose": True,
}

smart_scraper_graph = SmartScraperGraph(
    prompt="프로젝트와 설명을 모두 나열하세요",
    # 이미 다운로드된 HTML 코드가 있는 문자열도 허용
    source="https://perinim.github.io/projects",
    config=graph_config
)

result = smart_scraper_graph.run()
print(result)
```

출력은 다음과 같이 프로젝트와 설명의 목록이 될 것입니다:

```python
{'projects': [{'title': 'Rotary Pendulum RL', 'description': 'RL 알고리즘을 사용하여 실제 회전 진자를 제어하는 오픈 소스 프로젝트'}, {'title': 'DQN Implementation from scratch', 'description': '간단한 및 이중 진자를 훈련하기 위한 딥 Q-네트워크 알고리즘 개발'}, ...]}
사례 2: 혼합 모델을 사용하는 SearchGraph
우리는 LLM에 Groq를 사용하고, 임베딩에 Ollama를 사용합니다.
```

```python
from scrapegraphai.graphs import SearchGraph

# 그래프 구성 정의
graph_config = {
    "llm": {
        "model": "groq/gemma-7b-it",
        "api_key": "GROQ_API_KEY",
        "temperature": 0
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "base_url": "http://localhost:11434",  # Ollama URL 임의 설정
    },
    "max_results": 5,
}

# SearchGraph 인스턴스 생성
search_graph = SearchGraph(
    prompt="Chioggia의 전통 레시피를 모두 나열하세요",
    config=graph_config
)

# 그래프 실행
result = search_graph.run()
print(result)
출력은 다음과 같이 레시피 목록이 될 것입니다:
```

```python
{'recipes': [{'name': 'Sarde in Saòre'}, {'name': 'Bigoli in salsa'}, {'name': 'Seppie in umido'}, {'name': 'Moleche frite'}, {'name': 'Risotto alla pescatora'}, {'name': 'Broeto'}, {'name': 'Bibarasse in Cassopipa'}, {'name': 'Risi e bisi'}, {'name': 'Smegiassa Ciosota'}]}
사례 3: OpenAI를 사용하는 SpeechGraph
OpenAI API 키와 모델 이름만 전달하면 됩니다.
```

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
# SpeechGraph 인스턴스를 생성하고 실행합니다.
# ************************************************

speech_graph = SpeechGraph(
    prompt="프로젝트에 대한 자세한 오디오 요약을 만드세요.",
    source="https://perinim.github.io/projects/",
    config=graph_config,
)

result = speech_graph.run()
print(result)
```

출력은 페이지의 프로젝트 요약이 포함된 오디오 파일이 될 것입니다.

후원사

<div style="text-align: center;">
  <a href="https://serpapi.com?utm_source=scrapegraphai">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/serp_api_logo.png" alt="SerpAPI" style="width: 10%;">
  </a>
  <a href="https://dashboard.statproxies.com/?refferal=scrapegraph">
    <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/transparent_stat.png" alt="Stats" style="width: 15%;">
  </a>
</div>

## 🤝 기여

기여를 환영하며, 개선 사항을 논의하고 제안 사항을 주고받기 위해 우리의 Discord 서버에 참여하세요!

기여 가이드라인을 참조하십시오.

## 📈 로드맵

프로젝트 로드맵을 여기에서 확인하세요! 🚀

로드맵을 더 인터랙티브하게 시각화하고 싶으신가요? markdown 내용을 편집기에 복사하여 markmap 시각화를 확인하세요!

## ️ 기여자들



## 🎓 인용

우리의 라이브러리를 연구 목적으로 사용한 경우 다음과 같이 인용해 주세요:

text
Copia codice
  @misc{scrapegraph-ai,
    author = {Marco Perini, Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/VinciGit00/Scrapegraph-ai},
    note = {대규모 언어 모델을 활용한 Python 스크레이핑 라이브러리}
  }
저자들

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/logo_authors.png" alt="Authors_logos">
</p>
연락처
Marco Vinciguerra	
Marco Perini	
Lorenzo Padoan	

## 📜 라이선스

ScrapeGraphAI는 MIT License로 라이선스가 부여되었습니다. 자세한 내용은 LICENSE 파일을 참조하세요.

감사의 말

프로젝트에 기여한 모든 분들과 오픈 소스 커뮤니티에 감사드립니다.
ScrapeGraphAI는 데이터 탐색 및 연구 목적으로만 사용되어야 합니다. 우리는 라이브러리의 오용에 대해 책임을 지지 않습니다.