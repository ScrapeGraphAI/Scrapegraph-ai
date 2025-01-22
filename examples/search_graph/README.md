# Search Graph Example

This example shows how to implement a search graph for web content retrieval and analysis using Scrapegraph-ai.

## Features

- Web search integration
- Content relevance scoring
- Result filtering
- Data aggregation

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import SearchGraph

graph = SearchGraph()
results = graph.search("your search query")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `SERP_API_KEY`: Your SERP API key (optional)
