# 🕷️ ScrapeGraphAI: Yalnızca Bir Kez Kazıyın

[English](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/README.md) | [中文](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/chinese.md) | [日本語](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/japanese.md)
| [한국어](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/korean.md)
| [Русский](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/russian.md) | [Türkçe](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/docs/turkish.md)

[![İndirmeler](https://img.shields.io/pepy/dt/scrapegraphai?style=for-the-badge)](https://pepy.tech/project/scrapegraphai)
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen?style=for-the-badge)](https://github.com/pylint-dev/pylint)
[![Pylint](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/pylint.yml?label=Pylint&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/pylint.yml)
[![CodeQL](https://img.shields.io/github/actions/workflow/status/VinciGit00/Scrapegraph-ai/codeql.yml?label=CodeQL&logo=github&style=for-the-badge)](https://github.com/VinciGit00/Scrapegraph-ai/actions/workflows/codeql.yml)
[![Lisans: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![](https://dcbadge.vercel.app/api/server/gkxQDAjfeX)](https://discord.gg/gkxQDAjfeX)

ScrapeGraphAI, LLM ve grafik mantığını kullanarak web siteleri ve yerel belgeler (XML, HTML, JSON, Markdown vb.) için kazıma süreçleri oluşturan bir _web kazıma_ Python kütüphanesidir.

Sadece hangi bilgiyi çıkarmak istediğinizi söyleyin, kütüphane sizin için yapar!

<p align="center">
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/sgai-hero.png" alt="ScrapeGraphAI Hero" style="width: 100%;">
</p>

## 🚀 Hızlı Kurulum

Scrapegraph-ai için referans sayfası PyPI'nin resmi sayfasında mevcuttur: [pypi](https://pypi.org/project/scrapegraphai/).

```bash
pip install scrapegraphai

playwright install
```

**Not**: Diğer kütüphanelerle çakışmaları önlemek için kütüphaneyi sanal bir ortamda kurmanız önerilir 🐱

<details>
<summary><b>Opsiyonel Bağımlılıklar</b></summary>
Kütüphaneyi kurarken ek bağımlılıklar ekleyebilirsiniz:

- **Daha Fazla Dil Modeli**: Fireworks, Groq, Anthropic, Hugging Face ve Nvidia AI Endpoints gibi ek dil modelleri kurulur.

  Bu grup, Fireworks, Groq, Anthropic, Together AI, Hugging Face ve Nvidia AI Endpoints gibi ek dil modellerini kullanmanızı sağlar.

  ```bash
  pip install scrapegraphai[other-language-models]
  ```

- **Semantik Seçenekler**: Graphviz gibi gelişmiş semantik işleme araçlarını içerir.

  ```bash
  pip install scrapegraphai[more-semantic-options]
  ```

- **Tarayıcı Seçenekleri**: Browserbase gibi ek tarayıcı yönetim araçları/hizmetlerini içerir.

  ```bash
  pip install scrapegraphai[more-browser-options]
  ```

</details>

## 💻 Kullanım

Web sitesinden (veya yerel dosyadan) bilgi çıkarmak için kullanılabilecek birden fazla standart kazıma süreci vardır.

En yaygın olanı `SmartScraperGraph`'tır; bu, bir kullanıcı isteği ve kaynak URL'si verildiğinde tek bir sayfadan bilgi çıkarır.

```python
import json
from scrapegraphai.graphs import SmartScraperGraph

# Kazıma süreci için yapılandırmayı tanımlayın
graph_config = {
    "llm": {
        "api_key": "SİZİN_OPENAI_API_ANAHTARINIZ",
        "model": "openai/gpt-4o-mini",
    },
    "verbose": True,
    "headless": False,
}

# SmartScraperGraph örneğini oluşturun
smart_scraper_graph = SmartScraperGraph(
    prompt="Şirketin ne yaptığı, adı ve bir iletişim e-postası hakkında bazı bilgiler bulun.",
    source="https://scrapegraphai.com/",
    config=graph_config
)

# Süreci çalıştırın
result = smart_scraper_graph.run()
print(json.dumps(result, indent=4))
```

Çıktı aşağıdaki gibi bir sözlük olacaktır:

```python
{
    "company": "ScrapeGraphAI",
    "name": "ScrapeGraphAİ LLM kullanarak web sitelerinden ve yerel belgelerden içerik çıkarma",
    "contact_email": "contact@scrapegraphai.com"
}
```

Birden fazla sayfadan bilgi çıkarmak, Python scriptleri oluşturmak veya hatta ses dosyaları oluşturmak için kullanılabilecek diğer süreçler de vardır.

| Süreç Adı               | Açıklama                                                                                                 |
| ----------------------- | -------------------------------------------------------------------------------------------------------- |
| SmartScraperGraph       | Sadece bir kullanıcı isteği ve bir kaynak girişi gerektiren tek sayfalık kazıyıcı.                       |
| SearchGraph             | Bir arama motorunun en iyi n arama sonucundan bilgi çıkaran çok sayfalı kazıyıcı.                        |
| SpeechGraph             | Bir web sitesinden bilgi çıkaran ve bir ses dosyası oluşturan tek sayfalık kazıyıcı.                     |
| ScriptCreatorGraph      | Bir web sitesinden bilgi çıkaran ve bir Python scripti oluşturan tek sayfalık kazıyıcı.                  |
| SmartScraperMultiGraph  | Tek bir bilgi istemi ve kaynak listesi verilen birden çok sayfadan bilgi ayıklayan çok sayfalı kazıyıcı. |
| ScriptCreatorMultiGraph | Birden fazla sayfa veya kaynaktan bilgi çıkarmak için bir Python scripti oluşturan çok sayfalı kazıyıcı. |

Bu süreçlerin her biri için çoklu versiyon vardır. Bu, LLM çağrılarını paralel olarak yapmanızı sağlar.

**OpenAI**, **Groq**, **Azure** ve **Gemini** gibi API'ler aracılığıyla farklı LLM'leri kullanmak veya **Ollama** kullanarak yerel modelleri kullanmak mümkündür.

Yerel modelleri kullanmak istiyorsanız, [Ollama](https://ollama.com/) kurulu olduğundan ve **ollama pull** komutunu kullanarak modelleri indirdiğinizden emin olun.

## 🔍 Demo

Resmi Streamlit demosu:

[![My Skills](https://skillicons.dev/icons?i=react)](https://scrapegraph-ai-web-dashboard.streamlit.app)

Google Colab kullanarak doğrudan web üzerinde deneyin:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1sEZBonBMGP44CtO6GQTwAlL0BGJXjtfd?usp=sharing)

## 📖 Dokümantasyon

ScrapeGraphAI dokümantasyonuna [buradan](https://scrapegraph-ai.readthedocs.io/en/latest/) ulaşabilirsiniz.

Ayrıca Docusaurus'a [buradan](https://scrapegraph-doc.onrender.com/) göz atın.

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

## 🤝 Katkıda Bulunun

Projeye katkıda bulunmaktan çekinmeyin ve geliştirmeleri tartışmak ve bize önerilerde bulunmak için Discord sunucumuza katılın!

Lütfen [katkıda bulunma yönergelerine](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/CONTRIBUTING.md) bakın.

[![My Skills](https://skillicons.dev/icons?i=discord)](https://discord.gg/uJN7TYcpNa)
[![My Skills](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/company/scrapegraphai/)
[![My Skills](https://skillicons.dev/icons?i=twitter)](https://twitter.com/scrapegraphai)

## 📈 Telemetri

Paketimizin kalitesini ve kullanıcı deneyimini geliştirmek amacıyla anonim kullanım metrikleri topluyoruz. Bu veriler, iyileştirmelere öncelik vermemize ve uyumluluğu sağlamamıza yardımcı olur. İsterseniz, SCRAPEGRAPHAI_TELEMETRY_ENABLED=false ortam değişkenini ayarlayarak devre dışı bırakabilirsiniz. Daha fazla bilgi için lütfen [buraya](https://scrapegraph-ai.readthedocs.io/en/latest/scrapers/telemetry.html) bakın.

## ❤️ Katkıda Bulunanlar

[![Katkıda Bulunanlar](https://contrib.rocks/image?repo=VinciGit00/Scrapegraph-ai)](https://github.com/VinciGit00/Scrapegraph-ai/graphs/contributors)

## 🎓 Atıflar

Kütüphanemizi araştırma amaçlı kullandıysanız, lütfen bizi aşağıdaki referansla alıntılayın:

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
  <img src="https://raw.githubusercontent.com/VinciGit00/Scrapegraph-ai/main/docs/assets/logo_authors.png" alt="Yazarlar Logosu">
</p>

|                   | İletişim Bilgileri                                                                                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Marco Vinciguerra | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/marco-vinciguerra-7ba365242/) |
| Marco Perini      | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/perinim/)                     |
| Lorenzo Padoan    | [![Linkedin Badge](https://img.shields.io/badge/-Linkedin-blue?style=flat&logo=Linkedin&logoColor=white)](https://www.linkedin.com/in/lorenzo-padoan-4521a2154/)    |

## 📜 Lisans

ScrapeGraphAI, MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için [LİSANS](https://github.com/VinciGit00/Scrapegraph-ai/blob/main/LICENSE) dosyasına bakın.

## Teşekkürler

- Projeye katkıda bulunan tüm katılımcılara ve açık kaynak topluluğuna destekleri için teşekkür ederiz.
- ScrapeGraphAİ, yalnızca veri arama ve araştırma amacıyla kullanılmak üzere tasarlanmıştır. Kütüphanenin kötüye kullanılmasından sorumlu değiliz.
