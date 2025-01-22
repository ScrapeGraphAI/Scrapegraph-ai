# XML Scraper Graph Example

This example demonstrates how to use Scrapegraph-ai to extract and process XML data from web sources.

## Features

- XML data extraction
- XPath querying
- Data transformation
- Schema validation

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import XmlScraperGraph

graph = XmlScraperGraph()
xml_data = graph.scrape("https://example.com/feed.xml")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
