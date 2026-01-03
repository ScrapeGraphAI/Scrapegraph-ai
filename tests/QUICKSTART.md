# Testing Quick Start Guide

Get up and running with ScrapeGraphAI tests in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/ScrapeGraphAI/Scrapegraph-ai.git
cd Scrapegraph-ai

# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install
```

## Running Tests

### Quick Test (Unit Tests Only)
```bash
uv run pytest -m "unit or not integration"
```

### All Tests (Including Integration)
```bash
# Set API keys first
export OPENAI_APIKEY="your-key-here"

# Run all tests
uv run pytest --integration
```

### With Coverage
```bash
uv run pytest --cov=scrapegraphai --cov-report=html
open htmlcov/index.html  # View coverage report
```

## Writing Your First Test

### 1. Unit Test (Fast, No API Calls)

Create `tests/test_my_feature.py`:

```python
import pytest
from scrapegraphai.graphs import SmartScraperGraph

def test_my_feature(mock_llm_model, mock_server):
    """Test my feature with mocked dependencies."""
    url = mock_server.get_url("/products")

    # Test your feature here
    assert True
```

Run it:
```bash
uv run pytest tests/test_my_feature.py
```

### 2. Integration Test (With Real LLM)

```python
import pytest
from scrapegraphai.graphs import SmartScraperGraph

@pytest.mark.integration
@pytest.mark.requires_api_key
def test_real_scraping(openai_config, mock_server):
    """Test with real OpenAI API."""
    url = mock_server.get_url("/projects")

    scraper = SmartScraperGraph(
        prompt="List all projects",
        source=url,
        config=openai_config
    )

    result = scraper.run()
    assert result is not None
```

Run it:
```bash
export OPENAI_APIKEY="your-key"
uv run pytest tests/test_my_feature.py --integration
```

## Common Commands

```bash
# Run specific test
uv run pytest tests/test_my_feature.py::test_my_function

# Run tests matching pattern
uv run pytest -k "scraper"

# Run with verbose output
uv run pytest -v

# Run and stop at first failure
uv run pytest -x

# Show print statements
uv run pytest -s

# Run last failed tests
uv run pytest --lf

# Run slow tests
uv run pytest --slow

# Run benchmarks
uv run pytest --benchmark
```

## Using Fixtures

### Mock Server
```python
def test_with_mock_server(mock_server):
    url = mock_server.get_url("/products")
    # Use url in your test
```

### LLM Configs
```python
def test_with_openai(openai_config):
    scraper = SmartScraperGraph(
        prompt="...",
        source="...",
        config=openai_config
    )
```

### Temporary Files
```python
def test_with_temp_file(temp_json_file):
    # temp_json_file is a path to a temporary JSON file
    scraper = JSONScraperGraph(
        prompt="...",
        source=temp_json_file,
        config=config
    )
```

## Test Markers

Mark your tests appropriately:

```python
@pytest.mark.unit  # Fast unit test
@pytest.mark.integration  # Needs network
@pytest.mark.slow  # Takes > 5 seconds
@pytest.mark.benchmark  # Performance test
@pytest.mark.requires_api_key  # Needs API keys
```

## Debugging Tests

```bash
# Run with debugger
uv run pytest --pdb

# Drop into debugger on failure
uv run pytest --pdb -x

# Increase verbosity
uv run pytest -vv

# Show local variables on failure
uv run pytest -l
```

## Environment Setup

Create `.env` file in project root:

```bash
# LLM API Keys
OPENAI_APIKEY=sk-...
ANTHROPIC_APIKEY=sk-ant-...
GROQ_APIKEY=gsk_...

# Optional
AZURE_OPENAI_KEY=...
AZURE_OPENAI_ENDPOINT=https://...
GEMINI_APIKEY=...
```

## Next Steps

1. Read `tests/README_TESTING.md` for comprehensive documentation
2. Check `tests/integration/` for more examples
3. Review `tests/conftest.py` for available fixtures
4. See `TESTING_INFRASTRUCTURE.md` for architecture details

## Troubleshooting

### Tests Hanging
- Reduce timeout: `pytest --timeout=30`
- Check for network issues
- Verify API keys are valid

### Import Errors
```bash
# Reinstall dependencies
uv sync
```

### Playwright Errors
```bash
# Reinstall browsers
uv run playwright install
```

### API Rate Limits
- Use mock server for unit tests
- Add delays between integration tests
- Use `@pytest.mark.slow` for rate-limited tests

## Getting Help

- Check documentation: `tests/README_TESTING.md`
- Open an issue: [GitHub Issues](https://github.com/ScrapeGraphAI/Scrapegraph-ai/issues)
- Join Discord: [ScrapeGraphAI Discord](https://discord.gg/gkxQDAjfeX)

Happy testing! 🚀
