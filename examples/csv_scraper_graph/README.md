# CSV Scraper Graph Example

This example demonstrates how to use Scrapegraph-ai to extract data from web sources and save it in CSV format.

## Features

- Table data extraction
- CSV formatting
- Data cleaning
- Structured output

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import CsvScraperGraph

graph = CsvScraperGraph()
csv_data = graph.scrape("https://example.com/table")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
