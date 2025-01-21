# Script Generator Graph Example

This example demonstrates how to use Scrapegraph-ai to generate automation scripts based on data analysis.

## Features

- Automated script generation
- Task automation
- Code optimization
- Multiple language support

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import ScriptGeneratorGraph

graph = ScriptGeneratorGraph()
script = graph.generate("task description")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
