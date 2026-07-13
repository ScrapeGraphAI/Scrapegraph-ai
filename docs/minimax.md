# MiniMax

ScrapeGraphAI supports MiniMax-M3 and MiniMax-M2.7 through OpenAI-compatible
and Anthropic-compatible clients.

## Models

| Model | Context window | Input modalities | Thinking |
| --- | ---: | --- | --- |
| `MiniMax-M3` | 1,000,000 | Text, image, video | Adaptive or disabled; enabled when omitted |
| `MiniMax-M2.7` | 204,800 | Text | Always enabled |

## Endpoints

| Region | OpenAI-compatible base URL | Anthropic-compatible base URL |
| --- | --- | --- |
| Global | `https://api.minimax.io/v1` | `https://api.minimax.io/anthropic` |
| China | `https://api.minimaxi.com/v1` | `https://api.minimaxi.com/anthropic` |

The MiniMax adapter uses the global OpenAI-compatible endpoint by default.
Set `base_url` to use another OpenAI-compatible endpoint:

```python
import os

graph_config = {
    "llm": {
        "model": "minimax/MiniMax-M3",
        "api_key": os.environ["MINIMAX_API_KEY"],
        "base_url": os.environ.get(
            "MINIMAX_BASE_URL", "https://api.minimax.io/v1"
        ),
        "extra_body": {"thinking": {"type": "adaptive"}},
    },
}
```

For the Anthropic-compatible API, install `langchain-anthropic` and pass its
chat model through the existing `model_instance` configuration:

```python
import os

from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="MiniMax-M3",
    max_tokens=1000,
    api_key=os.environ["MINIMAX_API_KEY"],
    base_url=os.environ.get(
        "MINIMAX_ANTHROPIC_BASE_URL", "https://api.minimax.io/anthropic"
    ),
    thinking={"type": "adaptive"},
)

graph_config = {
    "llm": {
        "model": "MiniMax-M3",
        "model_instance": llm,
        "model_tokens": 1000000,
    },
}
```

Pass the Anthropic base URL exactly as shown. The client appends
`/v1/messages`; do not append `/v1` to the configured base URL.
