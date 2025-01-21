# Code Generator Graph Example

This example demonstrates how to use Scrapegraph-ai to generate code based on specifications and requirements.

## Features

- Code generation from specifications
- Multiple programming languages support
- Code documentation
- Best practices implementation

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import CodeGeneratorGraph

graph = CodeGeneratorGraph()
code = graph.generate("code specification")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
