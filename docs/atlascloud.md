## Atlas Cloud provider

[Atlas Cloud](https://www.atlascloud.ai/?utm_source=github&utm_medium=link&utm_campaign=Scrapegraph-ai) gives ScrapeGraphAI a drop-in OpenAI-compatible LLM backend, so you can keep the same graph configuration shape while switching to Atlas-hosted models.

For coding and agent workflows, Atlas Cloud also provides a budget-friendly [coding plan](https://www.atlascloud.ai/console/coding-plan).

### Quick setup

1. Export your Atlas credentials:

```bash
export ATLASCLOUD_API_KEY="<atlascloud-api-key>"
export ATLASCLOUD_MODEL="deepseek-ai/deepseek-v4-pro"
export ATLASCLOUD_MODEL_TOKENS="131072"
```

2. Configure ScrapeGraphAI with the `atlascloud/` provider prefix:

```python
import os

from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "api_key": os.environ["ATLASCLOUD_API_KEY"],
        "model": f'atlascloud/{os.getenv("ATLASCLOUD_MODEL", "deepseek-ai/deepseek-v4-pro")}',
        "model_tokens": int(os.getenv("ATLASCLOUD_MODEL_TOKENS", "131072")),
    },
    "verbose": True,
    "headless": False,
}

smart_scraper_graph = SmartScraperGraph(
    prompt="Extract the key product capabilities from the homepage",
    source="https://scrapegraphai.com/",
    config=graph_config,
)
```

### Notes

- ScrapeGraphAI routes `atlascloud/...` models through Atlas Cloud's OpenAI-compatible base URL: `https://api.atlascloud.ai/v1`
- Atlas reasoning models such as `deepseek-ai/deepseek-v4-pro` benefit from a larger `model_tokens` budget; set it explicitly in your config instead of relying on the generic fallback
- A runnable example lives at `examples/smart_scraper_graph/atlascloud/smart_scraper_atlascloud.py`

### Official Atlas LLM list

Official Atlas LLM list from `api.md` (59 models):

- Anthropic (Claude): `anthropic/claude-haiku-4.5-20251001`, `anthropic/claude-opus-4.8`, `anthropic/claude-sonnet-4.6`
- OpenAI (GPT): `openai/gpt-5.4`, `openai/gpt-5.5`
- Google (Gemini): `google/gemini-3.1-flash-lite`, `google/gemini-3.1-pro-preview`, `google/gemini-3.5-flash`
- Qwen: `qwen/qwen2.5-7b-instruct`, `Qwen/Qwen3-235B-A22B-Instruct-2507`, `qwen/qwen3-235b-a22b-thinking-2507`, `qwen/qwen3-30b-a3b`, `Qwen/Qwen3-30B-A3B-Instruct-2507`, `qwen/qwen3-30b-a3b-thinking-2507`, `qwen/qwen3-32b`, `qwen/qwen3-8b`, `Qwen/Qwen3-Coder`, `qwen/qwen3-coder-next`, `qwen/qwen3-max-2026-01-23`, `Qwen/Qwen3-Next-80B-A3B-Instruct`, `Qwen/Qwen3-Next-80B-A3B-Thinking`, `Qwen/Qwen3-VL-235B-A22B-Instruct`, `qwen/qwen3-vl-235b-a22b-thinking`, `qwen/qwen3-vl-30b-a3b-instruct`, `qwen/qwen3-vl-30b-a3b-thinking`, `qwen/qwen3-vl-8b-instruct`, `qwen/qwen3.5-122b-a10b`, `qwen/qwen3.5-27b`, `qwen/qwen3.5-35b-a3b`, `qwen/qwen3.5-397b-a17b`, `qwen/qwen3.6-35b-a3b`, `qwen/qwen3.6-plus`
- DeepSeek: `deepseek-ai/deepseek-ocr`, `deepseek-ai/deepseek-r1-0528`, `deepseek-ai/DeepSeek-V3-0324`, `deepseek-ai/DeepSeek-V3.1`, `deepseek-ai/DeepSeek-V3.1-Terminus`, `deepseek-ai/deepseek-v3.2`, `deepseek-ai/DeepSeek-V3.2-Exp`, `deepseek-ai/deepseek-v4-flash`, `deepseek-ai/deepseek-v4-pro`
- Moonshot (Kimi): `moonshotai/Kimi-K2-Instruct`, `moonshotai/Kimi-K2-Instruct-0905`, `moonshotai/Kimi-K2-Thinking`, `moonshotai/kimi-k2.5`, `moonshotai/kimi-k2.6`
- GLM: `zai-org/GLM-4.6`, `zai-org/glm-4.7`, `zai-org/glm-5`, `zai-org/glm-5-turbo`, `zai-org/glm-5.1`, `zai-org/glm-5v-turbo`
- MiniMax: `MiniMaxAI/MiniMax-M2`, `minimaxai/minimax-m2.1`, `minimaxai/minimax-m2.5`, `minimaxai/minimax-m2.7`
- xAI: `xai/grok-4.3`
- KAT: `kwaipilot/kat-coder-pro-v2`
- Other: `owl`
