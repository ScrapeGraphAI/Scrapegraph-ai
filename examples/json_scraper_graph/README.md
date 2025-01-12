# JSON Scraper Graph Example

This example demonstrates how to use Scrapegraph-ai to extract and process JSON data from web sources.

## Features

- JSON data extraction
- Schema validation
- Data transformation
- Structured output

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import JsonScraperGraph

graph = JsonScraperGraph()
json_data = graph.scrape("https://api.example.com/data")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
