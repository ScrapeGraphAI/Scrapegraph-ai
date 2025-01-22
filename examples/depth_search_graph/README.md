# Depth Search Graph Example

This example demonstrates how to use Scrapegraph-ai for deep web crawling and content exploration.

## Features

- Deep web crawling
- Content discovery
- Link analysis
- Recursive search

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import DepthSearchGraph

graph = DepthSearchGraph()
results = graph.search("https://example.com", depth=3)
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
