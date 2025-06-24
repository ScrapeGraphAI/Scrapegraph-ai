# Markdownify Graph Example

This example demonstrates how to use the Markdownify graph to convert HTML content to Markdown format.

## Features

- Convert HTML content to clean, readable Markdown
- Support for both URL and direct HTML input
- Maintains formatting and structure of the original content
- Handles complex HTML elements and nested structures

## Usage

```python
from scrapegraphai import Client
from scrapegraphai.logger import sgai_logger

# Set up logging
sgai_logger.set_logging(level="INFO")

# Initialize the client
sgai_client = Client(api_key="your-api-key")

# Example 1: Convert a website to Markdown
response = sgai_client.markdownify(
    website_url="https://example.com"
)
print(response.markdown)

# Example 2: Convert HTML content directly
html_content = """
<div>
    <h1>Hello World</h1>
    <p>This is a <strong>test</strong> paragraph.</p>
</div>
"""
response = sgai_client.markdownify(
    html_content=html_content
)
print(response.markdown)
```

## Parameters

The `markdownify` method accepts the following parameters:

- `website_url` (str, optional): The URL of the website to convert to Markdown
- `html_content` (str, optional): Direct HTML content to convert to Markdown

Note: You must provide either `website_url` or `html_content`, but not both.

## Response

The response object contains:

- `markdown` (str): The converted Markdown content
- `metadata` (dict): Additional information about the conversion process

## Error Handling

The graph handles various edge cases:

- Invalid URLs
- Malformed HTML
- Network errors
- Timeout issues

If an error occurs, it will be logged and raised with appropriate error messages.

## Best Practices

1. Always provide a valid URL or well-formed HTML content
2. Use appropriate logging levels for debugging
3. Handle the response appropriately in your application
4. Consider rate limiting for large-scale conversions
