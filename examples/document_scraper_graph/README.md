# Document Scraper Graph Example

This example demonstrates how to use Scrapegraph-ai to extract data from various document formats (PDF, DOC, DOCX, etc.).

## Features

- Multi-format document support
- Text extraction
- Document parsing
- Metadata extraction

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import DocumentScraperGraph

graph = DocumentScraperGraph()
content = graph.scrape("document.pdf")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
