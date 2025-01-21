# Custom Graph Example

This example demonstrates how to create and implement custom graphs using Scrapegraph-ai.

## Features

- Custom node creation
- Graph customization
- Pipeline configuration
- Custom data processing

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import CustomGraph

graph = CustomGraph()
graph.add_node("custom_node", CustomNode())
results = graph.process()
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
