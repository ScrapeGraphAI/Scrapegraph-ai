# 🕷️ ScrapeGraphAI: You Only Scrape Once

[English](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/README.md) | [中文](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/chinese.md) | [日本語](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/japanese.md)
| [한국어](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/korean.md)
| [Русский](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/russian.md) | [Turkish](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/turkish.md)

[![Downloads](https://img.shields.io/pepy/dt/scrapegraphai?style=for-the-badge)](https://pepy.tech/project/scrapegraphai)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen?style=for-the-badge)](https://github.com/pylint-dev/pylint)
[![Pylint](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/pylint.yml?label=Pylint&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/pylint.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/codeql.yml?label=CodeQL&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![](https://dcbadge.vercel.app/api/server/gkxQDAjfeX)](https://discord.gg/gkxQDAjfeX)

ScrapeGraphAI, web siteleri ve yerel belgeler (XML, HTML, JSON, Markdown vb.) için kazıma hatları oluşturmak üzere LLM ve doğrudan grafik mantığını kullanan bir web scraping Python kütüphanesidir.

Sadece çıkarmak istediğiniz bilgiyi belirtin; kütüphane bunu sizin için gerçekleştirecektir!

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/sgai-hero.png" alt="ScrapeGraphAI Hero" style="width: 100%;">
</p>

## 🚀 Hızlı kurulum

ScrapeGraphAI için referans sayfası, PyPI'nin resmi sayfasında mevcuttur: [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai

playwright install
```

**NOT**: Diğer kütüphanelerle çakışmaları önlemek için kütüphaneyi bir sanal ortamda kurmanız önerilir.

<details>
<summary><b>İsteğe Bağlı Bağımlılıklar</b></summary>

Kütüphane kurulumunda ek bağımlılıklar eklenebilir:

- <b>Daha Fazla Dil Modeli</b>: Fireworks, Groq, Anthropic, Hugging Face ve Nvidia AI Endpoints gibi ek dil modelleri yüklenir.

Bu grup, Fireworks, Groq, Anthropic, Together AI, Hugging Face ve Nvidia AI Endpoints gibi ek dil modellerini kullanmanıza olanak tanır.

```bash
  pip install scrapegraphai[other-language-models]
```

- <b>Anlamsal Seçenekler</b>: Bu grup, Graphviz gibi ileri düzey anlamsal işleme araçlarını içerir.

```bash
  pip install scrapegraphai[more-semantic-options]
```

- <b>Tarayıcı Seçenekleri</b>: Bu grup, Browserbase gibi ek tarayıcı yönetim araçlarını/hizmetlerini içerir.

```bash
 pip install scrapegraphai[more-browser-options]
```

</details>

## 💻 Kullanım

Bir web sitesinden (veya yerel dosyadan) bilgi almak için kullanılabilecek birçok standart kazıma hattı vardır.

En yaygın olanı, bir kullanıcı istemi ve bir kaynak URL'si verildiğinde tek bir sayfadan bilgi çıkaran `SmartScraperGraph`'tır.

```python
import json
from scrapegraphai.graphs import SmartScraperGraph

# Kazıma hattı için yapılandırmayı tanımlayın

graph_config = {
"llm": {
"api_key": "YOUR_OPENAI_APIKEY",
"model": "openai/gpt-4o-mini",
},
"verbose": True,
"headless": False,
}

# SmartScraperGraph örneğini oluşturun

smart_scraper_graph = SmartScraperGraph(
prompt="Şirketin ne yaptığı, adı ve iletişim e-postası hakkında bazı bilgiler bulun.",
source="https://scrapegraphai.com/",
config=graph_config
)

# Hattı çalıştırın

result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))

```

Çıktı, aşağıdaki gibi bir sözlük olacaktır:

```python
{
    "company": "ScrapeGraphAI",
    "name": "ScrapeGraphAI Extracting content from websites and local documents using LLM",
    "contact_email": "contact@scrapegraphai.com"
}
```

Birden fazla sayfadan bilgi ayıklamak, Python komut dosyaları oluşturmak ve hatta ses dosyaları oluşturmak için kullanılabilecek başka işlem hatları da vardır.

| Pipeline Name           | Description                                                                                                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------------- |
| SmartScraperGraph       | Single-page scraper that only needs a user prompt and an input source.                                        |
| SearchGraph             | Multi-page scraper that extracts information from the top n search results of a search engine.                |
| SpeechGraph             | Single-page scraper that extracts information from a website and generates an audio file.                     |
| ScriptCreatorGraph      | Single-page scraper that extracts information from a website and generates a Python script.                   |
| SmartScraperMultiGraph  | Multi-page scraper that extracts information from multiple pages given a single prompt and a list of sources. |
| ScriptCreatorMultiGraph | Multi-page scraper that generates a Python script for extracting information from multiple pages and sources. |

Bu grafiklerin her biri için çoklu versiyonu vardır. Bu, LLM'yi paralel olarak çağırmayı sağlar.

Farklı LLM'leri API'ler aracılığıyla kullanmak mümkündür, örneğin **OpenAI**, **Groq**, **Azure** ve **Gemini**, veya **Ollama** kullanarak yerel modeller.

Yerel modelleri kullanmak istiyorsanız, [Ollama](https://ollama.com/) kurulu olduğundan emin olun ve modelleri indirmek için **ollama pull** komutunu kullanın.

## 🔍 Demo

Resmi Streamlit demosu:

[![My Skills](https://skillicons.dev/icons?i=react)](https://scrapegraph-ai-web-dashboard.streamlit.app)

Bunu doğrudan web üzerinde Google Colab kullanarak deneyin:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

## 📖 Dokümantasyon

ScrapeGraphAI için dokümantasyonu [buradan](https://scrapegraph-ai.readthedocs.io/en/latest/) bulabilirsiniz.

Docusaurus'u da [buradan](https://scrapegraph-doc.onrender.com/) kontrol edin.

## 🏆 Sponsorlar

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

## 🤝 Katkıda Bulunma

Katkıda bulunmaktan çekinmeyin ve iyileştirmeleri tartışmak ve önerilerinizi iletmek için Discord sunucumuza katılın!

Lütfen [katkı sağlama yönergelerini](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/CONTRIBUTING.md) inceleyin.

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 📈 Telemetri

Paketin kalitesini ve kullanıcı deneyimini geliştirmek için anonim kullanım istatistikleri topluyoruz. Bu veriler, iyileştirmeleri önceliklendirmemize ve uyumluluğu sağlamamıza yardımcı olur. Eğer bu verileri almak istemiyorsanız, ortam değişkenini SCRAPEGRAPHAI_TELEMETRY_ENABLED=false olarak ayarlayın. Daha fazla bilgi için lütfen dokümantasyona [buradan](https://scrapegraph-ai.readthedocs.io/en/latest/scrapers/telemetry.html) bakın.

## ❤️ Katkıda Bulunanlar

[![Contributors](https://contrib.rocks/image?repo=VinciGit00/Scrapegraph-ai)](https://github.com/VinciGit00/Scrapegraph-ai/graphs/contributors)

## 🎓 Atıflar

Eğer kütüphanemizi araştırma amaçlı kullandıysanız, lütfen aşağıdaki referansla atıfta bulunun:

```text
  @misc{scrapegraph-ai,
    author = {Marco Perini, Lorenzo Padoan, Marco Vinciguerra},
    title = {Scrapegraph-ai},
    year = {2024},
    url = {https://github.com/VinciGit00/Scrapegraph-ai},
    note = {A Python library for scraping leveraging large language models}
  }
```

## Yazarlar

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/logo_authors.png" alt="Authors_logos">
</p>

|                   | İletişim Bilgisi                                                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Marco Vinciguerra | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/) |
| Marco Perini      | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/perinim/)                     |
| Lorenzo Padoan    | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)    |

## 📜 Lisans

ScrapeGraphAI, MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için [LİSANS](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/LICENSE) dosyasına bakın.

## Teşekkürler

- Projeye katkıda bulunan tüm katkı sahiplerine ve açık kaynak topluluğuna destekleri için teşekkür etmek isteriz.
- ScrapeGraphAI, yalnızca veri keşfi ve araştırma amaçları için kullanılmak üzere tasarlanmıştır. Kütüphanenin herhangi bir kötüye kullanımından sorumlu değiliz.
