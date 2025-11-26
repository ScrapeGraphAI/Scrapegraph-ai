# FetchNode Timeout Configuration

## Overview

The `FetchNode` in ScrapeGraphAI supports configurable timeouts for all blocking operations to prevent indefinite hangs when fetching web content or parsing files. This feature allows you to control execution time limits for:

- HTTP requests (when using `use_soup=True`)
- PDF file parsing
- ChromiumLoader operations

## Configuration

### Default Behavior

By default, `FetchNode` uses a **30-second timeout** for all blocking operations when a `node_config` is provided:

```python
from scrapegraphai.nodes import FetchNode

# Default 30-second timeout
node = FetchNode(
    input="url",
    output=["doc"],
    node_config={}
)
```

### Custom Timeout

You can specify a custom timeout value (in seconds) via the `timeout` parameter:

```python
# Custom 10-second timeout
node = FetchNode(
    input="url",
    output=["doc"],
    node_config={"timeout": 10}
)
```

### Disabling Timeout

To disable timeout and allow operations to run indefinitely, set `timeout` to `None`:

```python
# No timeout - operations will wait indefinitely
node = FetchNode(
    input="url",
    output=["doc"],
    node_config={"timeout": None}
)
```

### No Configuration

If you don't provide any `node_config`, the timeout defaults to `None` (no timeout):

```python
# No timeout (backward compatible)
node = FetchNode(
    input="url",
    output=["doc"],
    node_config=None
)
```

## Use Cases

### HTTP Requests

When `use_soup=True`, the timeout applies to `requests.get()` calls:

```python
node = FetchNode(
    input="url",
    output=["doc"],
    node_config={
        "use_soup": True,
        "timeout": 15  # HTTP request will timeout after 15 seconds
    }
)

state = {"url": "https://example.com"}
result = node.execute(state)
```

If the timeout is `None`, no timeout parameter is passed to `requests.get()`:

```python
node = FetchNode(
    input="url",
    output=["doc"],
    node_config={
        "use_soup": True,
        "timeout": None  # No timeout for HTTP requests
    }
)
```

### PDF Parsing

The timeout applies to PDF file parsing operations using `PyPDFLoader`:

```python
node = FetchNode(
    input="pdf",
    output=["doc"],
    node_config={
        "timeout": 60  # PDF parsing will timeout after 60 seconds
    }
)

state = {"pdf": "/path/to/large_document.pdf"}
try:
    result = node.execute(state)
except TimeoutError as e:
    print(f"PDF parsing took too long: {e}")
```

If parsing exceeds the timeout, a `TimeoutError` is raised with a descriptive message:

```
TimeoutError: PDF parsing exceeded timeout of 60 seconds
```

### ChromiumLoader

The timeout is automatically propagated to `ChromiumLoader` via `loader_kwargs`:

```python
node = FetchNode(
    input="url",
    output=["doc"],
    node_config={
        "timeout": 30,  # ChromiumLoader will use 30-second timeout
        "headless": True
    }
)

state = {"url": "https://example.com"}
result = node.execute(state)
```

If you need different timeout behavior for ChromiumLoader specifically, you can override it in `loader_kwargs`:

```python
node = FetchNode(
    input="url",
    output=["doc"],
    node_config={
        "timeout": 30,  # General timeout for other operations
        "loader_kwargs": {
            "timeout": 60  # ChromiumLoader gets 60-second timeout
        }
    }
)
```

## Graph Examples

### SmartScraperGraph

```python
from scrapegraphai.graphs import SmartScraperGraph

graph_config = {
    "llm": {
        "model": "gpt-3.5-turbo",
        "api_key": "your-api-key"
    },
    "timeout": 20  # 20-second timeout for fetch operations
}

smart_scraper = SmartScraperGraph(
    prompt="Extract all article titles",
    source="https://news.example.com",
    config=graph_config
)

result = smart_scraper.run()
```

### Custom Graph with FetchNode

```python
from scrapegraphai.nodes import FetchNode
from langgraph.graph import StateGraph

# Create a custom graph with timeout
fetch_node = FetchNode(
    input="url",
    output=["doc"],
    node_config={
        "timeout": 15,
        "headless": True
    }
)

# Add to graph...
```

## Best Practices

1. **Choose appropriate timeouts**: Consider the expected response time of your target websites
   - Fast APIs: 5-10 seconds
   - Regular websites: 15-30 seconds
   - Large PDFs or slow sites: 60+ seconds

2. **Handle TimeoutError**: Always wrap your code in try-except when using timeouts:

```python
try:
    result = node.execute(state)
except TimeoutError as e:
    logger.error(f"Operation timed out: {e}")
    # Handle timeout gracefully
```

3. **Use different timeouts for different operations**: Set higher timeouts for PDF parsing and lower for HTTP requests:

```python
# For PDFs
pdf_node = FetchNode("pdf", ["doc"], {"timeout": 120})

# For web pages
web_node = FetchNode("url", ["doc"], {"timeout": 15})
```

4. **Monitor timeout occurrences**: Log timeout errors to identify problematic sources:

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = node.execute(state)
except TimeoutError as e:
    logger.warning(f"Timeout for {state.get('url', 'unknown')}: {e}")
```

## Implementation Details

The timeout feature is implemented using:

- **HTTP requests**: `requests.get(url, timeout=X)` parameter
- **PDF parsing**: `concurrent.futures.ThreadPoolExecutor` with `future.result(timeout=X)`
- **ChromiumLoader**: Propagated via `loader_kwargs` dictionary

When `timeout=None`, no timeout constraints are applied, allowing operations to run until completion.

## Troubleshooting

### Timeout is too short

If you're seeing frequent timeout errors, increase the timeout value:

```python
node_config = {"timeout": 60}  # Increase from 30 to 60 seconds
```

### Need different timeouts for different operations

Use separate FetchNode instances with different configurations:

```python
fast_fetcher = FetchNode("url", ["doc"], {"timeout": 10})
slow_fetcher = FetchNode("pdf", ["doc"], {"timeout": 120})
```

### ChromiumLoader timeout not working

Ensure you're not overriding the timeout in `loader_kwargs`:

```python
# ❌ Wrong - explicit loader_kwargs timeout overrides node timeout
node_config = {
    "timeout": 30,
    "loader_kwargs": {"timeout": 10}  # This takes precedence
}

# ✅ Correct - let node timeout propagate
node_config = {
    "timeout": 30  # ChromiumLoader will use 30 seconds
}
```

## See Also

- [FetchNode API Documentation](../api/nodes/fetch_node.md)
- [Graph Configuration](./graph_configuration.md)
- [Error Handling](./error_handling.md)
