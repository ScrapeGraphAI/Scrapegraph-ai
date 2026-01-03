# ScrapeGraphAI Testing Infrastructure

Comprehensive testing infrastructure for ScrapeGraphAI with support for unit tests, integration tests, and performance benchmarks.

## Table of Contents

- [Overview](#overview)
- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Test Fixtures](#test-fixtures)
- [Performance Benchmarking](#performance-benchmarking)
- [Mock Server](#mock-server)
- [CI/CD Integration](#cicd-integration)

## Overview

The testing infrastructure includes:

- **Unit Tests**: Fast, isolated tests with mocked dependencies
- **Integration Tests**: Tests with real LLM providers and websites
- **Performance Benchmarks**: Track performance metrics and detect regressions
- **Mock HTTP Server**: Consistent testing without external dependencies
- **Multi-Provider Support**: Test compatibility across different LLM providers

## Test Organization

```
tests/
├── conftest.py                 # Shared fixtures and pytest configuration
├── pytest.ini                  # Pytest settings (in project root)
├── fixtures/
│   ├── mock_server/           # Mock HTTP server for testing
│   │   ├── __init__.py
│   │   └── server.py
│   ├── benchmarking.py        # Performance benchmarking utilities
│   ├── helpers.py             # Test utilities and helpers
│   ├── data/                  # Test data files
│   └── html/                  # HTML fixtures
├── integration/               # Integration tests
│   ├── test_smart_scraper_integration.py
│   ├── test_multi_graph_integration.py
│   └── test_file_formats_integration.py
├── graphs/                    # Graph-specific tests
├── nodes/                     # Node-specific tests
└── utils/                     # Utility tests
```

## Running Tests

### All Tests

```bash
pytest
```

### Unit Tests Only

```bash
pytest -m "unit or not integration"
```

### Integration Tests

```bash
pytest --integration
```

### With Coverage

```bash
pytest --cov=scrapegraphai --cov-report=html
```

### Performance Benchmarks

```bash
pytest --benchmark -m benchmark
```

### Slow Tests

```bash
pytest --slow
```

### Specific Test File

```bash
pytest tests/integration/test_smart_scraper_integration.py
```

### Verbose Output

```bash
pytest -v
```

## Test Fixtures

### LLM Provider Fixtures

Pre-configured fixtures for all supported LLM providers:

```python
def test_with_openai(openai_config):
    """Use OpenAI configuration."""
    scraper = SmartScraperGraph(
        prompt="...",
        source="...",
        config=openai_config
    )
```

Available fixtures:
- `openai_config` - OpenAI GPT-3.5
- `openai_gpt4_config` - OpenAI GPT-4
- `ollama_config` - Ollama (local)
- `anthropic_config` - Anthropic Claude
- `groq_config` - Groq
- `azure_config` - Azure OpenAI
- `gemini_config` - Google Gemini

### Mock LLM Fixtures

For unit testing without API calls:

```python
def test_with_mock_llm(mock_llm_model, mock_embedder_model):
    """Use mocked LLM for fast unit tests."""
    # Test logic here
```

### File Fixtures

Temporary files for testing:

```python
def test_json_scraping(temp_json_file):
    """Use temporary JSON file."""
    scraper = JSONScraperGraph(
        prompt="...",
        source=temp_json_file,
        config=config
    )
```

Available fixtures:
- `temp_json_file`
- `temp_html_file`
- `temp_xml_file`
- `temp_csv_file`

### Mock HTTP Server

Local HTTP server for consistent testing:

```python
def test_with_mock_server(mock_server):
    """Use mock HTTP server."""
    url = mock_server.get_url("/products")

    scraper = SmartScraperGraph(
        prompt="Extract products",
        source=url,
        config=config
    )
```

Available endpoints:
- `/` - Home page
- `/products` - Products listing
- `/projects` - Projects listing
- `/api/data.json` - JSON endpoint
- `/api/data.xml` - XML endpoint
- `/api/data.csv` - CSV endpoint
- `/slow` - Slow response (2s delay)
- `/error/404` - 404 error
- `/error/500` - 500 error
- `/rate-limited` - Rate limiting simulation
- `/pagination?page=N` - Paginated content

## Performance Benchmarking

### Using the Benchmark Tracker

```python
def test_performance(benchmark_tracker):
    """Track performance metrics."""
    import time

    start = time.perf_counter()
    # ... run scraping ...
    end = time.perf_counter()

    from tests.fixtures.benchmarking import BenchmarkResult

    result = BenchmarkResult(
        test_name="my_test",
        execution_time=end - start,
        token_usage=1000,
        api_calls=2,
        success=True
    )

    benchmark_tracker.record(result)
```

### Generating Reports

After running benchmarks:

```python
# In your test or conftest.py
tracker.save_results()
report = tracker.generate_report()
print(report)
```

### Comparing Against Baseline

```bash
# Save baseline
pytest --benchmark -m benchmark
cp benchmark_results/benchmark_results.json baseline.json

# Run tests and compare
pytest --benchmark -m benchmark

# Compare programmatically
from tests.fixtures.benchmarking import pytest_benchmark_compare
comparison = pytest_benchmark_compare(
    Path("baseline.json"),
    Path("benchmark_results/benchmark_results.json")
)
```

## Test Markers

### Available Markers

- `@pytest.mark.unit` - Unit tests (fast, no external deps)
- `@pytest.mark.integration` - Integration tests (require network)
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.benchmark` - Performance benchmarks
- `@pytest.mark.requires_api_key` - Tests requiring API keys
- `@pytest.mark.llm_provider(name)` - Tests for specific LLM provider

### Usage Example

```python
@pytest.mark.integration
@pytest.mark.requires_api_key
@pytest.mark.slow
def test_comprehensive_scraping(openai_config):
    """This test requires API keys and network access."""
    # Test implementation
```

## Environment Variables

Set these environment variables for integration tests:

```bash
# LLM API Keys
export OPENAI_APIKEY="sk-..."
export ANTHROPIC_APIKEY="sk-ant-..."
export GROQ_APIKEY="gsk_..."
export GEMINI_APIKEY="..."

# Azure OpenAI
export AZURE_OPENAI_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://..."

# Test Configuration
export TEST_WEBSITE_URL="https://scrapegrah-ai-website-for-tests.onrender.com"
export OLLAMA_BASE_URL="http://localhost:11434"
```

## CI/CD Integration

### GitHub Actions

The test suite runs automatically on:
- Push to main, pre/beta, dev branches
- Pull requests
- Daily scheduled runs
- Manual workflow dispatch

### Test Jobs

1. **Unit Tests**: Run on multiple OS and Python versions
2. **Integration Tests**: Test with real LLM providers
3. **Performance Benchmarks**: Track performance metrics
4. **Code Quality**: Linting, formatting, type checking

### Viewing Results

- Test results are uploaded as artifacts
- Coverage reports are sent to Codecov
- Performance benchmarks are saved for comparison

## Writing New Tests

### Unit Test Template

```python
import pytest
from unittest.mock import Mock, patch

class TestMyFeature:
    @pytest.fixture
    def setup(self):
        """Setup fixture for tests."""
        return {"data": "value"}

    def test_my_function(self, setup, mock_llm_model):
        """Test description."""
        # Arrange
        # Act
        # Assert
```

### Integration Test Template

```python
import pytest
from scrapegraphai.graphs import SmartScraperGraph

@pytest.mark.integration
@pytest.mark.requires_api_key
class TestMyIntegration:
    def test_real_scraping(self, openai_config, mock_server):
        """Test with real LLM provider."""
        url = mock_server.get_url("/test-page")

        scraper = SmartScraperGraph(
            prompt="Extract data",
            source=url,
            config=openai_config
        )

        result = scraper.run()

        assert result is not None
        assert isinstance(result, dict)
```

### Benchmark Test Template

```python
import pytest
import time
from tests.fixtures.benchmarking import BenchmarkResult

@pytest.mark.benchmark
class TestMyBenchmark:
    def test_performance(self, benchmark_tracker, openai_config):
        """Benchmark test description."""
        start = time.perf_counter()

        # Run operation to benchmark

        end = time.perf_counter()

        result = BenchmarkResult(
            test_name="my_benchmark",
            execution_time=end - start,
            success=True
        )

        benchmark_tracker.record(result)
```

## Troubleshooting

### Tests Timeout

Increase timeout in pytest.ini or per-test:

```python
@pytest.mark.timeout(120)  # 2 minutes
def test_long_running():
    pass
```

### API Rate Limits

Use mock server or implement rate limiting in tests:

```python
from tests.fixtures.helpers import RateLimitHelper

rate_limiter = RateLimitHelper(max_requests=5, time_window=60)
```

### Flaky Tests

Mark tests as flaky and allow retries:

```python
@pytest.mark.flaky(reruns=3, reruns_delay=2)
def test_sometimes_fails():
    pass
```

## Best Practices

1. **Use appropriate markers** - Mark tests correctly for proper filtering
2. **Mock external dependencies** - Use mock server and fixtures
3. **Test isolation** - Each test should be independent
4. **Clear assertions** - Use helper functions for better error messages
5. **Performance tracking** - Use benchmarking for critical paths
6. **Documentation** - Document test purpose and requirements
7. **Cleanup** - Use fixtures and context managers for proper cleanup

## Contributing

When adding tests:

1. Follow existing test structure and naming conventions
2. Add appropriate markers
3. Document test requirements (API keys, network, etc.)
4. Update this README if adding new test infrastructure
5. Ensure tests pass in CI before submitting PR

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [ScrapeGraphAI Documentation](https://scrapegraph-ai.readthedocs.io/)
