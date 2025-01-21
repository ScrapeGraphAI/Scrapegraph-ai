# Omni Scraper Graph Example

This example demonstrates how to use Scrapegraph-ai for universal web scraping across multiple data formats.

## Features

- Multi-format data extraction (JSON, XML, HTML, CSV)
- Automatic format detection
- Unified data output
- Content transformation

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import OmniScraperGraph

graph = OmniScraperGraph()
data = graph.scrape("https://example.com/data")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
