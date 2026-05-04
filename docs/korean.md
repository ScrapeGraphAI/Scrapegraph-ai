## 🚀 **더 빠르고 간단한 대규모 스크래핑 방법(단 5줄의 코드)을 찾고 계신가요?** [**ScrapeGraphAI.com**](https://scrapegraphai.com/?utm_source=github&utm_medium=readme&utm_campaign=oss_cta&utm_content=top_banner)의 향상된 버전을 확인해보세요! 🚀

---

# 🕷️ ScrapeGraphAI: 한 방에 끝내는 웹스크래핑

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

[ScrapeGraphAI](https://scrapegraphai.com)는 웹 사이트와 로컬 문서(XML, HTML, JSON, Markdown 등)에 대한 스크래핑 파이프라인을 만들기 위해 LLM 및 직접 그래프 로직을 사용하는 파이썬 웹스크래핑 라이브러리입니다.

추출하려는 정보를 말하기만 하면 라이브러리가 알아서 처리해 줍니다!

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/sgai-hero.png" alt="ScrapeGraphAI Hero" style="width: 100%;">
</p>


## 🚀 통합
ScrapeGraphAI는 인기 있는 프레임워크 및 도구와의 원활한 통합을 제공하여 스크래핑 능력을 향상시킵니다. 파이썬이든 Node.js로 개발하든, LLM 프레임워크를 사용하든, 노코드 플랫폼이든 저희의 포괄적인 통합 옵션을 제공합니다.

더 많은 정보는 다음 [링크](https://scrapegraphai.com)에서 확인할 수 있습니다

**통합**:
- **API**: [문서](https://docs.scrapegraphai.com/introduction)
- **SDKs**: [Python](https://docs.scrapegraphai.com/sdks/python), [Node](https://docs.scrapegraphai.com/sdks/javascript)
- **LLM 프레임워크**: [Langchain](https://docs.scrapegraphai.com/integrations/langchain), [Llama Index](https://docs.scrapegraphai.com/integrations/llamaindex), [Crew.ai](https://docs.scrapegraphai.com/integrations/crewai), [Agno](https://docs.scrapegraphai.com/integrations/agno), [CamelAI](https://github.com/camel-ai/camel)
- **로우코드 프레임워크**: [Pipedream](https://pipedream.com/apps/scrapegraphai), [Bubble](https://bubble.io/plugin/scrapegraphai-1745408893195x213542371433906180), [Zapier](https://zapier.com/apps/scrapegraphai/integrations), [n8n](http://localhost:5001/dashboard), [Dify](https://dify.ai), [Toolhouse](https://app.toolhouse.ai/mcp-servers/scrapegraph_smartscraper)
- **MCP 서버**:  [링크](https://smithery.ai/server/@ScrapeGraphAI/scrapegraph-mcp)

## 🚀 빠른 설치

Scrapegraph-ai에 대한 참조 페이지는 PyPI의 공식 페이지에서 확인할 수 있습니다: [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai

# 중요 (웹사이트 콘텐츠 가져오기용)
playwright install
```

**참고**: 다른 라이브러리와의 충돌을 피하기 위해 라이브러리를 가상 환경에 설치하는 것이 좋습니다 🐱


## 💻 사용법
웹사이트(또는 로컬 파일)에서 정보를 추출하기 위해 사용할 수 있는 여러 표준 스크래핑 파이프라인이 있습니다.

가장 일반적인 것은 `SmartScraperGraph`로, 사용자 프롬프트와 소스 URL이 주어진 단일 페이지에서 정보를 추출합니다.


```python
from scrapegraphai.graphs import SmartScraperGraph

# 스크래핑 파이프라인에 대한 구성 정의
graph_config = {
    "llm": {
        "model": "ollama/llama3.2",
        "model_tokens": 8192,
        "format": "json",
    },
    "verbose": True,
    "headless": False,
}

# SmartScraperGraph 인스턴스 생성
smart_scraper_graph = SmartScraperGraph(
    prompt="웹페이지에서 유용한 정보를 추출하세요. 회사가 하는 일에 대한 설명, 창립자 및 소셜 미디어 링크를 포함하세요",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# 파이프라인 실행
result = smart_scraper_graph.run()

import json
print(json.dumps(result, indent=4))
```

> [!NOTE]
> OpenAI나 다른 모델들은 LLM 설정만 바꾸면 됩니다!
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


출력은 다음과 같은 dictionary 형태가 될 것입니다:

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
여러 페이지에서 정보를 추출하거나, Python 스크립트를 생성하거나, 심지어 오디오 파일을 생성하는 데 사용할 수 있는 다른 파이프라인도 있습니다.

| 파이프라인 이름           | 설명                                                                                                      |
|-------------------------|------------------------------------------------------------------------------------------------------------------|
| SmartScraperGraph       | 사용자 프롬프트와 입력 소스만 있으면 되는 단일 페이지 스크래퍼입니다.                                           |
| SearchGraph             | 검색 엔진의 상위 n개 검색 결과에서 정보를 추출하는 다중 페이지 스크래퍼입니다.                  |
| SpeechGraph             | 웹사이트에서 정보를 추출하고 오디오 파일을 생성하는 단일 페이지 스크래퍼입니다.                       |
| ScriptCreatorGraph      | 웹사이트에서 정보를 추출하고 파이썬 스크립트를 생성하는 단일 페이지 스크래퍼입니다.                     |
| SmartScraperMultiGraph  | 단일 프롬프트와 출처 목록이 주어지면 여러 페이지에서 정보를 추출하는 다중 페이지 스크래퍼입니다.    |
| ScriptCreatorMultiGraph | 여러 페이지와 소스에서 정보를 추출하기 위한 파이썬 스크립트를 생성하는 다중 페이지 스크래퍼입니다.     |

각 그래프에는 다중 버전이 있습니다. 이를 통해 LLM을 병렬로 호출할 수 있습니다.

OpenAI, Groq, Azure, Gemini와 같은 API를 통해 다양한 LLM을 사용할 수 있으며, Ollama를 이용한 로컬 모델도 가능합니다.

로컬 모델을 사용하려면 [Ollama](https://ollama.com/)를 설치하고 ollama pull 명령을 사용하여 모델을 다운로드해야 합니다.


## 📖 문서

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

ScrapeGraphAI 관련 문서는 [여기](https://docs.scrapegraphai.com/introduction)에서 확인하실 수 있습니다.

## 🤝 기여

자유롭게 기여하고 Discord 서버에 참여하여 개선 사항을 논의하고 제안해 주세요!

[기여 가이드라인](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/CONTRIBUTING.md)을 참고하세요.

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 🔗 ScrapeGraph API & SDKs
시스템에 ScrapeGraph를 통합하기 위한 빠른 솔루션을 찾고 있다면, [여기!](https://dashboard.scrapegraphai.com/login)에서 강력한 API를 확인해 보세요.

[![API Banner](https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/api_banner.png)](https://dashboard.scrapegraphai.com/login)

Python과 Node.js SDK를 제공하여 프로젝트에 쉽게 통합할 수 있습니다. 아래에서 확인해 보세요.

| SDK       | 언어 | GitHub 링크                                                                 |
|-----------|----------|-----------------------------------------------------------------------------|
| Python SDK | Python   | [scrapegraph-py](https://github.com/ScrapeGraphAI/scrapegraph-sdk/tree/main/scrapegraph-py) |
| Node.js SDK | Node.js  | [scrapegraph-js](https://github.com/ScrapeGraphAI/scrapegraph-sdk/tree/main/scrapegraph-js) |

공식 API 문서는 [여기](https://docs.scrapegraphai.com/introduction)에서 확인할 수 있습니다.

## 🔥 벤치마크

Firecrawl 벤치마크 [Firecrawl benchmark](https://github.com/firecrawl/scrape-evals/pull/3)에 따르면, ScrapeGraph는 시장에서 최고의 페처입니다!

![here](assets/histogram.png)

## 📈 텔레메트리
저희는 패키지의 품질과 사용자 경험을 향상시키기 위해 익명의 사용 지표를 수집합니다. 이 데이터는 개선 사항의 우선순위를 정하고 호환성을 보장하는 데 도움이 됩니다. 옵트아웃하려면 환경 변수 SCRAPEGRAPHAI_TELEMETRY_ENABLED=false를 설정하세요. 자세한 내용은 [여기](https://docs.scrapegraphai.com/introduction)에서 설명서를 참조하세요.

## ❤️ 기여자들
[![Contributors](https://contrib.rocks/image?repo=VinciGit00/Scrapegraph-ai)](https://github.com/VinciGit00/Scrapegraph-ai/graphs/contributors)

## 🎓 인용
우리의 라이브러리를 연구 목적으로 사용한 경우 다음과 같이 인용해 주세요:
```text
  @misc{scrapegraph-ai,
    author = {Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/VinciGit00/Scrapegraph-ai},
    note = {대규모 언어 모델을 활용한 스크래핑용 Python 라이브러리}
  }
```

## 저자들

|                    | 연락처        |
|--------------------|---------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/)    |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)  |

## 📜 라이선스

ScrapeGraphAI는 MIT License로 배포되었습니다. 자세한 내용은 [LICENSE](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/LICENSE) 파일을 참조하세요.

## 감사의 말

- 프로젝트에 기여한 모든 분들과 오픈 소스 커뮤니티에 감사드립니다.
- ScrapeGraphAI는 데이터 탐색 및 연구 목적으로만 사용되어야 합니다. 우리는 라이브러리의 오용에 대해 책임을 지지 않습니다.

Made with ❤️ by [ScrapeGraph AI](https://scrapegraphai.com)

[Scarf tracking](https://static.scarf.sh/a.png?x-pxid=102d4b8c-cd6a-4b9e-9a16-d6d141b9212d)
