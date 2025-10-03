# ScrapeGraphAI Services Guide

Complete reference guide for all available graph services (pipelines) in ScrapeGraphAI and their parameters.

---

## Table of Contents

1. [Basic Scrapers](#basic-scrapers)
2. [Multi-Source Scrapers](#multi-source-scrapers)
3. [Search-Based Scrapers](#search-based-scrapers)
4. [Specialized Scrapers](#specialized-scrapers)
5. [Script Generators](#script-generators)
6. [Common Configuration Parameters](#common-configuration-parameters)

---

## Basic Scrapers

### SmartScraperGraph

Extracts information from a single webpage using natural language prompts.

**Parameters:**
- `prompt` (str): Natural language description of what to extract
- `source` (str): URL (starts with `http`) or local file path
- `config` (dict): Configuration dictionary (see [Common Configuration](#common-configuration-parameters))
- `schema` (Optional[BaseModel]): Pydantic model for structured output

**Example:**
```python
from scrapegraphai.graphs import SmartScraperGraph

scraper = SmartScraperGraph(
    prompt="List all the attractions in Chioggia",
    source="https://en.wikipedia.org/wiki/Chioggia",
    config={
        "llm": {
            "model": "openai/gpt-3.5-turbo",
            "api_key": "your-api-key"
        },
        "verbose": True
    }
)
result = scraper.run()
```

---

### SmartScraperLiteGraph

Lightweight version of SmartScraperGraph with reduced token usage and faster execution.

**Parameters:**
- Same as `SmartScraperGraph`

**Use Case:** When you need faster scraping with lower costs and don't need deep analysis.

---

### JSONScraperGraph

Extracts information from JSON files using natural language queries.

**Parameters:**
- `prompt` (str): Query about the JSON data
- `source` (str): Path to `.json` file or directory containing JSON files
- `config` (dict): Configuration dictionary
- `schema` (Optional[BaseModel]): Pydantic model for structured output

**Example:**
```python
from scrapegraphai.graphs import JSONScraperGraph

scraper = JSONScraperGraph(
    prompt="Extract all product names and prices",
    source="data/products.json",
    config={
        "llm": {
            "model": "openai/gpt-3.5-turbo",
            "api_key": "your-api-key"
        }
    }
)
result = scraper.run()
```

---

### CSVScraperGraph

Extracts information from CSV files using natural language queries.

**Parameters:**
- `prompt` (str): Query about the CSV data
- `source` (str): Path to `.csv` file or directory containing CSV files
- `config` (dict): Configuration dictionary
- `schema` (Optional[BaseModel]): Pydantic model for structured output

---

### XMLScraperGraph

Extracts information from XML files using natural language queries.

**Parameters:**
- `prompt` (str): Query about the XML data
- `source` (str): Path to `.xml` file or directory containing XML files
- `config` (dict): Configuration dictionary
- `schema` (Optional[BaseModel]): Pydantic model for structured output

---

### DocumentScraperGraph

Extracts information from various document formats (PDF, DOCX, TXT, etc.).

**Parameters:**
- `prompt` (str): Query about the document
- `source` (str): Path to document file
- `config` (dict): Configuration dictionary
- `schema` (Optional[BaseModel]): Pydantic model for structured output

---

## Multi-Source Scrapers

### SmartScraperMultiGraph

Scrapes multiple URLs in parallel and aggregates results.

**Parameters:**
- `prompt` (str): What to extract from each URL
- `source` (List[str]): List of URLs to scrape
- `config` (dict): Configuration dictionary
- `schema` (Optional[BaseModel]): Pydantic model for structured output

**Example:**
```python
from scrapegraphai.graphs import SmartScraperMultiGraph

scraper = SmartScraperMultiGraph(
    prompt="Extract the main topic and summary",
    source=[
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ],
    config={
        "llm": {"model": "openai/gpt-4", "api_key": "your-key"}
    }
)
result = scraper.run()
```

---

### SmartScraperMultiLiteGraph

Lightweight version of SmartScraperMultiGraph for faster, cost-effective multi-source scraping.

**Parameters:**
- Same as `SmartScraperMultiGraph`

---

### SmartScraperMultiConcatGraph

Scrapes multiple URLs and concatenates their content before processing (useful for related pages).

**Parameters:**
- Same as `SmartScraperMultiGraph`

---

### JSONScraperMultiGraph

Processes multiple JSON files in parallel.

**Parameters:**
- `prompt` (str): Query about the JSON data
- `source` (List[str]): List of paths to JSON files
- `config` (dict): Configuration dictionary
- `schema` (Optional[BaseModel]): Pydantic model for structured output

---

### CSVScraperMultiGraph

Processes multiple CSV files in parallel.

**Parameters:**
- Same as `JSONScraperMultiGraph` but for CSV files

---

### XMLScraperMultiGraph

Processes multiple XML files in parallel.

**Parameters:**
- Same as `JSONScraperMultiGraph` but for XML files

---

### DocumentScraperMultiGraph

Processes multiple documents in parallel.

**Parameters:**
- Same as `JSONScraperMultiGraph` but for various document formats

---

## Search-Based Scrapers

### SearchGraph

Searches the internet, scrapes top results, and aggregates information.

**Parameters:**
- `prompt` (str): Search query and what to extract
- `config` (dict): Configuration dictionary with **search-specific parameters**:
  - `max_results` (int): Number of search results to scrape (default: 3)
  - `search_engine` (str): Search engine to use - `"duckduckgo"`, `"bing"`, `"searxng"`, `"serper"` (default: "duckduckgo")
  - `serper_api_key` (str): API key for Serper search engine
  - **`region`** (str): Country/region code (e.g., `"it-it"` for Italy, `"us-en"` for US)
  - **`language`** (str): Language code (e.g., `"en"`, `"it"`, `"es"`) (default: "en")
  - **`timelimit`** (str): Time filter for results - `"d"` (day), `"w"` (week), `"m"` (month), `"y"` (year)
- `schema` (Optional[BaseModel]): Pydantic model for structured output

**Example:**
```python
from scrapegraphai.graphs import SearchGraph

scraper = SearchGraph(
    prompt="What is Gruppo Chiesi pharmaceutical company known for?",
    config={
        "llm": {
            "model": "openai/gpt-4",
            "api_key": "your-key"
        },
        "max_results": 5,
        "search_engine": "duckduckgo",
        "region": "it-it",           # Search in Italian region
        "language": "it",             # Italian language
        "timelimit": "y",             # Past year results
        "verbose": True
    }
)
result = scraper.run()

# Get URLs that were scraped
urls = scraper.get_considered_urls()
```

**Debug Output (when `verbose=True`):**
```
🧠 DEBUG: Original User Prompt: What is Gruppo Chiesi pharmaceutical company known for?
🔍 DEBUG: LLM Simplified Search Query: Gruppo Chiesi pharmaceutical company
🌐 DEBUG: URLs found by duckduckgo (5 results): ['url1', 'url2', ...]
```

---

### SearchLinkGraph

Searches within a specific website and scrapes matching pages.

**Parameters:**
- `prompt` (str): What to search for and extract
- `source` (str): Base URL of the website to search within
- `config` (dict): Same as `SearchGraph` (includes region, language, timelimit)
- `schema` (Optional[BaseModel]): Pydantic model for structured output

**Example:**
```python
from scrapegraphai.graphs import SearchLinkGraph

scraper = SearchLinkGraph(
    prompt="Find all product pages about laptops",
    source="https://example-store.com",
    config={
        "llm": {"model": "openai/gpt-4", "api_key": "your-key"},
        "max_results": 10
    }
)
result = scraper.run()
```

---

### DepthSearchGraph

Performs recursive search by following links up to a specified depth.

**Parameters:**
- `prompt` (str): What to search for and extract
- `config` (dict): Same as `SearchGraph` plus depth-related parameters
- `schema` (Optional[BaseModel]): Pydantic model for structured output

**Use Case:** Deep research tasks requiring exploration of linked content.

---

### OmniSearchGraph

Advanced search that combines multiple search strategies and data sources.

**Parameters:**
- `prompt` (str): Complex search query
- `config` (dict): Same as `SearchGraph` with additional omni-search parameters
- `schema` (Optional[BaseModel]): Pydantic model for structured output

---

## Specialized Scrapers

### OmniScraperGraph

Scrapes both text and images from webpages, with image analysis capabilities.

**Parameters:**
- `prompt` (str): What to extract (can reference images)
- `source` (str): URL or local file path
- `config` (dict): Configuration dictionary with:
  - `max_images` (int): Maximum number of images to process (default: 5)
  - Standard config parameters
- `schema` (Optional[BaseModel]): Pydantic model for structured output

**Example:**
```python
from scrapegraphai.graphs import OmniScraperGraph

scraper = OmniScraperGraph(
    prompt="List attractions in Chioggia and describe their pictures",
    source="https://en.wikipedia.org/wiki/Chioggia",
    config={
        "llm": {"model": "openai/gpt-4o", "api_key": "your-key"},
        "max_images": 10
    }
)
result = scraper.run()
```

---

### ScreenshotScraperGraph

Takes a screenshot of a webpage and extracts information from the visual content.

**Parameters:**
- `prompt` (str): What to extract from the screenshot
- `source` (str): URL to screenshot
- `config` (dict): Configuration dictionary
- `schema` (Optional[BaseModel]): Pydantic model for structured output

**Use Case:** Scraping dynamic content, charts, or visual layouts that are hard to extract from HTML.

---

### SpeechGraph

Converts webpage content to speech/audio output.

**Parameters:**
- `prompt` (str): What content to convert to speech
- `source` (str): URL or local file path
- `config` (dict): Configuration dictionary with audio settings
- `schema` (Optional[BaseModel]): Pydantic model for structured output

---

## Script Generators

### ScriptCreatorGraph

Generates a web scraping script based on the prompt and target webpage.

**Parameters:**
- `prompt` (str): What you want the script to scrape
- `source` (str): URL or local file to analyze
- `config` (dict): Configuration dictionary with:
  - **`library`** (str): Scraping library to use - `"beautifulsoup"`, `"scrapy"`, `"playwright"`, etc. (required)
  - Standard config parameters
- `schema` (Optional[BaseModel]): Pydantic model for structured output

**Example:**
```python
from scrapegraphai.graphs import ScriptCreatorGraph

generator = ScriptCreatorGraph(
    prompt="Create a script to extract all product names and prices",
    source="https://example-store.com/products",
    config={
        "llm": {"model": "openai/gpt-4", "api_key": "your-key"},
        "library": "beautifulsoup"
    }
)
script = generator.run()
print(script)  # Outputs Python scraping code
```

---

### ScriptCreatorMultiGraph

Generates scraping scripts for multiple webpages.

**Parameters:**
- `prompt` (str): What the script should scrape
- `source` (List[str]): List of URLs to analyze
- `config` (dict): Same as `ScriptCreatorGraph` (requires `library`)
- `schema` (Optional[BaseModel]): Pydantic model for structured output

---

### CodeGeneratorGraph

Generates custom code for data processing pipelines.

**Parameters:**
- `prompt` (str): Description of the code to generate
- `source` (str): Data source or example
- `config` (dict): Configuration dictionary
- `schema` (Optional[BaseModel]): Pydantic model for structured output

---

## Common Configuration Parameters

All graphs accept a `config` dictionary with the following parameters:

### LLM Configuration (Required)

```python
"llm": {
    "model": "openai/gpt-4",           # Model identifier
    "api_key": "your-api-key",         # API key for the provider
    "temperature": 0,                  # Creativity (0-1)
    "max_tokens": 2000,                # Max tokens per request
}
```

**Supported Models:**
- OpenAI: `"openai/gpt-4"`, `"openai/gpt-3.5-turbo"`, `"openai/gpt-4o"`
- Anthropic: `"anthropic/claude-3-opus"`, `"anthropic/claude-3-sonnet"`
- Google: `"google/gemini-pro"`
- Local: `"ollama/llama2"`, `"ollama/mistral"`
- And many more via LangChain integration

---

### General Configuration

```python
{
    "verbose": True,                   # Show execution details (default: False)
    "headless": True,                  # Run browser in headless mode (default: True)
    "timeout": 480,                    # Request timeout in seconds (default: 480)
    "cache_path": "./cache",           # Path to cache directory (default: False)
}
```

---

### Browser & Loading Configuration

```python
{
    "loader_kwargs": {
        "proxy": "http://proxy:8080",  # Proxy server
        "wait_for": "networkidle",     # Wait condition for page load
        "headers": {...}               # Custom HTTP headers
    },
    "storage_state": "auth.json",      # Browser authentication state file
    "browser_base": {...},             # BrowserBase integration config
    "scrape_do": {...},                # ScrapeDo integration config
}
```

---

### Search Configuration (SearchGraph, SearchLinkGraph, DepthSearchGraph)

```python
{
    "max_results": 5,                  # Number of search results (default: 3)
    "search_engine": "duckduckgo",     # Search engine: duckduckgo, bing, searxng, serper
    "serper_api_key": "your-key",      # Required for serper engine

    # NEW: Enhanced search parameters
    "region": "it-it",                 # Region code (e.g., "us-en", "it-it", "de-de")
    "language": "en",                  # Language code (default: "en")
    "timelimit": "y",                  # Time filter: "d", "w", "m", "y" (day/week/month/year)
}
```

---

### Embedder Configuration (Optional - for RAG-based graphs)

```python
{
    "embedder": {
        "model": "openai/text-embedding-3-small",
        "api_key": "your-api-key"
    }
}
```

---

### Burr Integration (Optional - for workflow tracking)

```python
{
    "burr_kwargs": {
        "app_instance_id": "my-scraping-job",
        "project_name": "web-scraper"
    }
}
```

---

## Complete Example: SearchGraph with All Parameters

```python
from scrapegraphai.graphs import SearchGraph
from pydantic import BaseModel, Field

# Define output schema
class CompanyInfo(BaseModel):
    name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    headquarters: str = Field(description="Location of headquarters")
    recent_news: list[str] = Field(description="Recent news items")

# Configure and run
scraper = SearchGraph(
    prompt="Find recent news and information about Gruppo Chiesi pharmaceutical company",
    config={
        # LLM config
        "llm": {
            "model": "openai/gpt-4",
            "api_key": "your-openai-key",
            "temperature": 0
        },

        # Search config
        "max_results": 5,
        "search_engine": "duckduckgo",
        "region": "it-it",           # Italian region
        "language": "it",            # Italian language
        "timelimit": "m",            # Past month

        # General config
        "verbose": True,
        "headless": True,
        "timeout": 300,

        # Browser config
        "loader_kwargs": {
            "wait_for": "networkidle"
        }
    },
    schema=CompanyInfo
)

result = scraper.run()
print(result)

# Get URLs that were considered
urls = scraper.get_considered_urls()
print(f"Scraped {len(urls)} URLs: {urls}")
```

---

## Error Handling & Resilience

ScrapeGraphAI now includes enhanced error handling:

1. **GraphIteratorNode** (multi-source scraping): Individual site failures won't crash the entire pipeline
2. **Search parameters**: Better quality results reduce parsing errors
3. **Debug logging**: Use `verbose=True` to troubleshoot issues

---

## Tips & Best Practices

1. **Choose the right graph**: Use `SmartScraperGraph` for single pages, `SearchGraph` for research tasks
2. **Use schemas**: Define Pydantic schemas for consistent, structured output
3. **Set region/language**: For localized content, always set `region` and `language`
4. **Use timelimit**: Filter search results by time to get fresh content
5. **Enable verbose mode**: Set `verbose=True` during development to see what's happening
6. **Start with lite versions**: Use `SmartScraperLiteGraph` for faster testing
7. **Cache results**: Set `cache_path` to avoid re-scraping during development

---

## Support & Documentation

- **Official Docs**: https://docs.scrapegraphai.com
- **GitHub**: https://github.com/VinciGit00/Scrapegraph-ai
- **Discord Community**: https://discord.gg/gkxQDAjfeX
- **API Documentation**: https://scrapegraphai.com

---

**Last Updated**: 2025-01-10
