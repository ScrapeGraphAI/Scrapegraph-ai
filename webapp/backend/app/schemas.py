from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class BackendType(str, Enum):
    playwright = "playwright"
    crawl4ai = "crawl4ai"
    obscura = "obscura"


class LLMConfig(BaseModel):
    provider: str = Field(..., description="e.g. ollama, openai, deepseek")
    model: str = Field(..., description="e.g. llama3.2, gpt-4o")
    api_key: str | None = None
    model_tokens: int = 8192


class Crawl4AIConfig(BaseModel):
    output_format: str = "markdown"
    headless: bool = True
    page_timeout: int = 30000


class ObscuraConfig(BaseModel):
    cdp_url: str = "ws://127.0.0.1:9222/devtools/browser"
    auto_start: str | None = None


class BackendConfig(BaseModel):
    type: BackendType = BackendType.playwright
    headless: bool = True
    proxy: dict | None = None
    crawl4ai: Crawl4AIConfig | None = None
    obscura: ObscuraConfig | None = None


class ScrapeRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    llm: LLMConfig
    backend: BackendConfig = Field(default_factory=BackendConfig)


class ScrapeResponse(BaseModel):
    status: str
    data: Any = None
    error: str | None = None
    execution_info: Any = None


class ModelInfo(BaseModel):
    ollama_models: list[str] = []
    providers: list[str] = [
        "openai", "azure_openai", "ollama", "deepseek",
        "anthropic", "google_genai", "groq", "mistralai",
        "bedrock", "oneapi", "xai", "nvidia", "clod", "minimax",
    ]


class LogEntry(BaseModel):
    ts: str
    level: str
    module: str
    message: str
    traceback: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"
