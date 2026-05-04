## 🚀 **正在寻找更快、更简单的规模化抓取方式（只需5行代码）？** 查看我们在 [**ScrapeGraphAI.com**](https://scrapegraphai.com/?utm_source=github&utm_medium=readme&utm_campaign=oss_cta&utm_content=top_banner) 的增强版本！🚀

---

# 🕷️ ScrapeGraphAI: 只需抓取一次

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

[ScrapeGraphAI](https://scrapegraphai.com) 是一个*网络爬虫* Python 库，使用大型语言模型和直接图逻辑为网站和本地文档（XML，HTML，JSON，Markdown 等）创建爬取管道。

只需告诉库您想提取哪些信息，它将为您完成！

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/sgai-hero.png" alt="ScrapeGraphAI Hero" style="width: 100%;">
</p>


## 🚀 集成
ScrapeGraphAI 提供与流行框架和工具的无缝集成，以增强您的抓取能力。无论您使用 Python 还是 Node.js 构建，使用 LLM 框架，还是使用无代码平台，我们都为您提供全面的集成选项。

您可以在以下[链接](https://scrapegraphai.com)找到更多信息

**集成**：
- **API**: [文档](https://docs.scrapegraphai.com/introduction)
- **SDKs**: [Python](https://docs.scrapegraphai.com/sdks/python), [Node](https://docs.scrapegraphai.com/sdks/javascript)
- **LLM 框架**: [Langchain](https://docs.scrapegraphai.com/integrations/langchain), [Llama Index](https://docs.scrapegraphai.com/integrations/llamaindex), [Crew.ai](https://docs.scrapegraphai.com/integrations/crewai), [Agno](https://docs.scrapegraphai.com/integrations/agno), [CamelAI](https://github.com/camel-ai/camel)
- **低代码框架**: [Pipedream](https://pipedream.com/apps/scrapegraphai), [Bubble](https://bubble.io/plugin/scrapegraphai-1745408893195x213542371433906180), [Zapier](https://zapier.com/apps/scrapegraphai/integrations), [n8n](http://localhost:5001/dashboard), [Dify](https://dify.ai), [Toolhouse](https://app.toolhouse.ai/mcp-servers/scrapegraph_smartscraper)
- **MCP 服务器**:  [链接](https://smithery.ai/server/@ScrapeGraphAI/scrapegraph-mcp)

## 🚀 快速安装

Scrapegraph-ai 的参考页面可以在 PyPI 的官方网站上找到: [pypi](https://pypi.org/project/scrapegraphai/)。

```bash
pip install scrapegraphai

# 重要（用于获取网站内容）
playwright install
```

**注意**: 建议在虚拟环境中安装该库，以避免与其他库发生冲突 🐱


## 💻 用法
有多种标准抓取管道可用于从网站（或本地文件）提取信息。

最常见的是 `SmartScraperGraph`，它在给定用户提示和源 URL 的情况下从单个页面提取信息。


```python
from scrapegraphai.graphs import SmartScraperGraph

# 定义抓取管道的配置
graph_config = {
    "llm": {
        "model": "ollama/llama3.2",
        "model_tokens": 8192,
        "format": "json",
    },
    "verbose": True,
    "headless": False,
}

# 创建 SmartScraperGraph 实例
smart_scraper_graph = SmartScraperGraph(
    prompt="从网页中提取有用信息，包括公司描述、创始人和社交媒体链接",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# 运行管道
result = smart_scraper_graph.run()

import json
print(json.dumps(result, indent=4))
```

> [!NOTE]
> 对于 OpenAI 和其他模型，您只需要更改 llm 配置！
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


输出将是一个类似以下的字典：

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
还有其他管道可用于从多个页面提取信息、生成 Python 脚本，甚至生成音频文件。

| 管道名称           | 描述                                                                                                      |
|-------------------------|------------------------------------------------------------------------------------------------------------------|
| SmartScraperGraph       | 单页抓取器，只需要用户提示和输入源。                                           |
| SearchGraph             | 多页抓取器，从搜索引擎的前 n 个搜索结果中提取信息。                  |
| SpeechGraph             | 单页抓取器，从网站提取信息并生成音频文件。                       |
| ScriptCreatorGraph      | 单页抓取器，从网站提取信息并生成 Python 脚本。                     |
| SmartScraperMultiGraph  | 多页抓取器，在给定单个提示和源列表的情况下从多个页面提取信息。    |
| ScriptCreatorMultiGraph | 多页抓取器，生成用于从多个页面和源提取信息的 Python 脚本。     |

对于这些图中的每一个，都有多版本。它允许并行调用 LLM。

可以通过 API 使用不同的 LLM，例如 **OpenAI**、**Groq**、**Azure** 和 **Gemini**，或使用 **Ollama** 的本地模型。

如果您想使用本地模型，请记住安装 [Ollama](https://ollama.com/) 并使用 **ollama pull** 命令下载模型。


## 📖 文档

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

ScrapeGraphAI 的文档可以在[这里](https://docs.scrapegraphai.com/introduction)找到。

## 🤝 贡献

欢迎贡献并加入我们的 Discord 服务器与我们讨论改进和提出建议！

请参阅[贡献指南](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/CONTRIBUTING.md)。

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 🔗 ScrapeGraph API & SDKs
如果您正在寻找快速解决方案来将 ScrapeGraph 集成到您的系统中，请查看我们的强大 API [这里！](https://dashboard.scrapegraphai.com/login)

[![API Banner](https://raw.githubusercontent.com/ScrapeGraphAI/Scrapegraph-ai/main/docs/assets/api_banner.png)](https://dashboard.scrapegraphai.com/login)

我们提供 Python 和 Node.js 的 SDK，使您可以轻松集成到您的项目中。请在下面查看：

| SDK       | 语言 | GitHub 链接                                                                 |
|-----------|----------|-----------------------------------------------------------------------------|
| Python SDK | Python   | [scrapegraph-py](https://github.com/ScrapeGraphAI/scrapegraph-sdk/tree/main/scrapegraph-py) |
| Node.js SDK | Node.js  | [scrapegraph-js](https://github.com/ScrapeGraphAI/scrapegraph-sdk/tree/main/scrapegraph-js) |

官方 API 文档可以在[这里](https://docs.scrapegraphai.com/introduction)找到。

## 🔥 基准测试

根据 Firecrawl 基准测试 [Firecrawl benchmark](https://github.com/firecrawl/scrape-evals/pull/3)，ScrapeGraph 是市场上最好的抓取工具！

![here](assets/histogram.png)

## 📈 遥测
我们收集匿名使用指标以增强我们包的质量和用户体验。这些数据帮助我们确定改进的优先级并确保兼容性。如果您希望退出，请设置环境变量 SCRAPEGRAPHAI_TELEMETRY_ENABLED=false。有关更多信息，请参阅[这里](https://docs.scrapegraphai.com/introduction)的文档。

## ❤️ 贡献者
[![Contributors](https://contrib.rocks/image?repo=VinciGit00/Scrapegraph-ai)](https://github.com/VinciGit00/Scrapegraph-ai/graphs/contributors)

## 🎓 引用
如果您将我们的库用于研究目的，请使用以下参考文献引用我们：
```text
  @misc{scrapegraph-ai,
    author = {Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/VinciGit00/Scrapegraph-ai},
    note = {一个利用大型语言模型进行爬取的 Python 库}
  }
```
## 作者

|                    | 联系信息         |
|--------------------|----------------------|
| Marco Vinciguerra  | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/)    |
| Lorenzo Padoan     | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)  |

## 📜 许可证

ScrapeGraphAI 采用 MIT 许可证。更多信息请查看 [LICENSE](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/LICENSE) 文件。

## 鸣谢

- 我们要感谢所有项目贡献者和开源社区的支持。
- ScrapeGraphAI 仅用于数据探索和研究目的。我们不对任何滥用该库的行为负责。

Made with ❤️ by [ScrapeGraph AI](https://scrapegraphai.com)

[Scarf tracking](https://static.scarf.sh/a.png?x-pxid=102d4b8c-cd6a-4b9e-9a16-d6d141b9212d)
