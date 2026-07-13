# Troubleshooting & Common Issues

This guide addresses the most frequently reported extraction problems and how to fix them. Most issues come from three root causes: the schema is stricter than the page content, the target site blocks automated requests, or the model/token configuration is wrong.

## 1. Output is empty, contains `NA`, or some fields are `null`

This is the single most common problem (see issues #1102, #893, #598, #926).

### Why it happens
ScrapeGraphAI builds a `pydantic` model from your `schema` (or from the prompt when no schema is given). When a field is declared as required but the LLM cannot find a confident value on the page, the model either returns `null` for that field or the whole result collapses to `{}` / `"NA"`. The official behavior is: **a required field that cannot be extracted yields `null`** — it is not an error by default.

### Fixes
- **Make fields optional.** Prefer `Optional[...]` / `None` defaults so missing data does not break the model:
  ```python
  from pydantic import BaseModel, Field
  from typing import Optional, List

  class CompanyInfo(BaseModel):
      description: Optional[str] = None
      founders: Optional[List[str]] = None
      social_media_links: Optional[dict] = None
  ```
- **Loosen the prompt.** Vague prompts ("extract useful info") produce vague, often empty output. Be explicit: "Extract the company description (1-2 sentences), the names of all founders, and every social media URL present in the page footer."
- **Verify the page actually contains the data.** Many "empty" results are pages that load content via JavaScript or require scrolling. Use `headless: False` and a real browser to confirm the text is in the DOM/HTML.
- **Beware `PromptTemplate` variable errors (#926).** If you see `PromptTemplate must have the following variables`, a `{` or `}` in your prompt is being interpreted as a template variable. Escape literal braces as `{{` `}}` or move the text out of the template.
- **Add `model_tokens`.** If the model context is too small the output is truncated or empty; set `model_tokens` explicitly (see section 3).

## 2. `pydantic` validation / `ValidationError` (#598)

### Why it happens
The LLM returns JSON whose types do not match the `schema` (e.g. a string where a list is expected, or an object where a string is expected). With strict `pydantic` v2 settings this raises instead of coercing.

### Fixes
- Make schema types permissive (`Optional`, `Union[str, list]`).
- Reduce nesting; flat schemas extract more reliably.
- If you only need raw text, drop the schema and let the graph return a string.

## 3. Token-limit / "exceeds the model context window" errors (#768)

### Why it happens
The default context size is `8192` tokens unless the model is found in `models_tokens`. Long pages + long prompts overflow the window.

### Fixes
- Set `model_tokens` in the `llm` config to your model's real context size:
  ```python
  graph_config = {
      "llm": {
          "model": "openai/gpt-4o",
          "model_tokens": 128000,
          "api_key": "...",
      },
      "verbose": True,
  }
  ```
- Reduce `max_results` / chunk the source, or use a model with a larger context.

## 4. Anti-bot / `403`, cookie walls, CAPTCHA (#283, #313)

### Why it happens
Some sites block the default fetch (requests/Playwright without realistic headers) or render content only after JS execution / interaction.

### Fixes
- Use `headless: False` so you can pass challenges manually during development.
- Add a real `user_agent` and, when needed, proxy settings in `graph_config`.
- For JS-heavy pages, ensure Playwright is installed (`playwright install`) and consider scrolling/loading strategies.
- Respect `robots.txt` and site terms; scrape responsibly.

## 5. `Provider ... is not supported` / `Model not supported`

### Why it happens
The `model` string prefix must match a known provider (e.g. `openai/...`, `ollama/...`, `deepseek/...`). An unknown prefix raises `ValueError`.

### Fixes
- Use the `provider/model` form: `"model": "openai/gpt-4o-mini"`.
- For OpenAI-compatible gateways (OpenRouter, Atlas Cloud, OneApi, etc.) prefix with the registered provider, e.g. `"openrouter/anthropic/claude-3.5-sonnet"`.
- If your provider is not registered, pass a ready `model_instance` instead of a string.

## Still stuck?
Open a Discussion with: the exact `graph_config`, the `prompt`, the source URL, and the full error/traceback. Most "empty output" reports are resolved by making schema fields optional and confirming the data is present in the rendered page.
