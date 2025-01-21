# Speech Graph Example

This example demonstrates how to use Scrapegraph-ai for speech processing and analysis.

## Features

- Speech-to-text conversion
- Audio processing
- Text analysis
- Sentiment analysis

## Setup

1. Install required dependencies
2. Copy `.env.example` to `.env`
3. Configure your API keys in the `.env` file

## Usage

```python
from scrapegraphai.graphs import SpeechGraph

graph = SpeechGraph()
text = graph.process("audio_file.mp3")
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `WHISPER_API_KEY`: Your Whisper API key (optional)
