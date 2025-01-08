# Smart Scraper Example

This example demonstrates how to use Scrapegraph-ai for intelligent web scraping with automatic content detection and extraction.

## Features

- Intelligent content detection
- Automatic data extraction
- Content classification
- Clean data output

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your OpenAI API key in the `.env` file

## Usage

```python
from scrapegraphai.graphs import SmartScraperGraph

graph = SmartScraperGraph()
results = graph.scrape("https://example.com")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
