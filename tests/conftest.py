"""
Pytest configuration and shared fixtures for ScrapeGraphAI tests.

This module provides:
- LLM provider fixtures for all supported models
- Mock server fixtures for consistent testing
- Test data fixtures
- Performance benchmarking utilities
"""

import json
import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock

import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "fixtures" / "data"
TEST_HTML_DIR = Path(__file__).parent / "fixtures" / "html"


# ============================================================================
# LLM Provider Fixtures
# ============================================================================


@pytest.fixture
def openai_config() -> Dict[str, Any]:
    """OpenAI configuration for testing."""
    api_key = os.getenv("OPENAI_APIKEY", "test-key")
    return {
        "llm": {
            "api_key": api_key,
            "model": "gpt-3.5-turbo",
            "temperature": 0,
        },
        "verbose": False,
        "headless": True,
    }


@pytest.fixture
def openai_gpt4_config() -> Dict[str, Any]:
    """OpenAI GPT-4 configuration for testing."""
    api_key = os.getenv("OPENAI_APIKEY", "test-key")
    return {
        "llm": {
            "api_key": api_key,
            "model": "gpt-4",
            "temperature": 0,
        },
        "verbose": False,
        "headless": True,
    }


@pytest.fixture
def ollama_config() -> Dict[str, Any]:
    """Ollama configuration for testing."""
    return {
        "llm": {
            "model": "ollama/llama3.2",
            "temperature": 0,
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        },
        "verbose": False,
        "headless": True,
    }


@pytest.fixture
def anthropic_config() -> Dict[str, Any]:
    """Anthropic Claude configuration for testing."""
    api_key = os.getenv("ANTHROPIC_APIKEY", "test-key")
    return {
        "llm": {
            "api_key": api_key,
            "model": "anthropic/claude-3-sonnet",
            "temperature": 0,
        },
        "verbose": False,
        "headless": True,
    }


@pytest.fixture
def groq_config() -> Dict[str, Any]:
    """Groq configuration for testing."""
    api_key = os.getenv("GROQ_APIKEY", "test-key")
    return {
        "llm": {
            "api_key": api_key,
            "model": "groq/llama3-8b-8192",
            "temperature": 0,
        },
        "verbose": False,
        "headless": True,
    }


@pytest.fixture
def azure_config() -> Dict[str, Any]:
    """Azure OpenAI configuration for testing."""
    return {
        "llm": {
            "api_key": os.getenv("AZURE_OPENAI_KEY", "test-key"),
            "model": "azure_openai/gpt-35-turbo",
            "api_base": os.getenv("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com/"),
            "api_version": "2024-02-15-preview",
            "temperature": 0,
        },
        "verbose": False,
        "headless": True,
    }


@pytest.fixture
def gemini_config() -> Dict[str, Any]:
    """Google Gemini configuration for testing."""
    api_key = os.getenv("GEMINI_APIKEY", "test-key")
    return {
        "llm": {
            "api_key": api_key,
            "model": "gemini/gemini-pro",
            "temperature": 0,
        },
        "verbose": False,
        "headless": True,
    }


@pytest.fixture(params=[
    "openai_config",
    "ollama_config",
    "anthropic_config",
    "groq_config",
])
def multi_llm_config(request):
    """Parametrized fixture that tests against multiple LLM providers."""
    return request.getfixturevalue(request.param)


# ============================================================================
# Mock LLM Fixtures
# ============================================================================


@pytest.fixture
def mock_llm_model():
    """Mock LLM model for unit testing."""
    mock = Mock()
    mock.model_name = "mock-model"
    mock.predict = Mock(return_value="Mocked LLM response")
    mock.invoke = Mock(return_value="Mocked LLM response")
    return mock


@pytest.fixture
def mock_embedder_model():
    """Mock embedder model for unit testing."""
    mock = Mock()
    mock.embed_documents = Mock(return_value=[[0.1, 0.2, 0.3]])
    mock.embed_query = Mock(return_value=[0.1, 0.2, 0.3])
    return mock


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_html() -> str:
    """Sample HTML content for testing."""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Test Heading</h1>
        <div class="content">
            <p>This is a test paragraph with some content.</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
                <li>Item 3</li>
            </ul>
        </div>
        <div class="projects">
            <article class="project">
                <h2>Project Alpha</h2>
                <p>Description of Project Alpha</p>
            </article>
            <article class="project">
                <h2>Project Beta</h2>
                <p>Description of Project Beta</p>
            </article>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_json_data() -> Dict[str, Any]:
    """Sample JSON data for testing."""
    return {
        "name": "Test Company",
        "description": "A test company description",
        "employees": [
            {"name": "Alice", "role": "Engineer"},
            {"name": "Bob", "role": "Designer"},
        ],
        "founded": "2020",
        "location": "San Francisco",
    }


@pytest.fixture
def sample_xml() -> str:
    """Sample XML content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
    <company>
        <name>Test Company</name>
        <employees>
            <employee>
                <name>Alice</name>
                <role>Engineer</role>
            </employee>
            <employee>
                <name>Bob</name>
                <role>Designer</role>
            </employee>
        </employees>
    </company>
    """


@pytest.fixture
def sample_csv() -> str:
    """Sample CSV content for testing."""
    return """name,role,department
Alice,Engineer,Engineering
Bob,Designer,Design
Charlie,Manager,Operations"""


# ============================================================================
# File-based Fixtures
# ============================================================================


@pytest.fixture
def temp_json_file(tmp_path, sample_json_data):
    """Create a temporary JSON file for testing."""
    json_file = tmp_path / "test_data.json"
    json_file.write_text(json.dumps(sample_json_data, indent=2))
    return str(json_file)


@pytest.fixture
def temp_html_file(tmp_path, sample_html):
    """Create a temporary HTML file for testing."""
    html_file = tmp_path / "test_page.html"
    html_file.write_text(sample_html)
    return str(html_file)


@pytest.fixture
def temp_xml_file(tmp_path, sample_xml):
    """Create a temporary XML file for testing."""
    xml_file = tmp_path / "test_data.xml"
    xml_file.write_text(sample_xml)
    return str(xml_file)


@pytest.fixture
def temp_csv_file(tmp_path, sample_csv):
    """Create a temporary CSV file for testing."""
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text(sample_csv)
    return str(csv_file)


# ============================================================================
# Performance Benchmarking Fixtures
# ============================================================================


@pytest.fixture
def benchmark_config():
    """Configuration for performance benchmarking."""
    return {
        "warmup_runs": 1,
        "test_runs": 3,
        "timeout": 60,
    }


@pytest.fixture
def performance_tracker():
    """Track performance metrics across tests."""
    metrics = {
        "execution_times": [],
        "token_usage": [],
        "api_calls": [],
    }
    return metrics


# ============================================================================
# Mock Server Fixtures
# ============================================================================


@pytest.fixture
def mock_server():
    """Start a mock HTTP server for testing."""
    from tests.fixtures.mock_server.server import MockHTTPServer

    server = MockHTTPServer(host="localhost", port=8888)
    server.start()
    yield server
    server.stop()


@pytest.fixture
def mock_server_url(mock_server):
    """Get the base URL for the mock server."""
    return mock_server.get_url()


@pytest.fixture
def mock_website_url():
    """URL for the mock test website."""
    # This can be overridden with an environment variable
    return os.getenv(
        "TEST_WEBSITE_URL",
        "https://scrapegrah-ai-website-for-tests.onrender.com"
    )


# ============================================================================
# Pytest Markers and Configuration
# ============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (requires network)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "llm_provider(name): mark test for specific LLM provider"
    )
    config.addinivalue_line(
        "markers", "requires_api_key: mark test as requiring API keys"
    )
    config.addinivalue_line(
        "markers", "benchmark: mark test as performance benchmark"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection based on markers and CLI options."""
    skip_integration = pytest.mark.skip(reason="use --integration to run")
    skip_slow = pytest.mark.skip(reason="use --slow to run")
    skip_requires_api = pytest.mark.skip(reason="requires API keys")

    for item in items:
        # Skip integration tests unless --integration flag is passed
        if "integration" in item.keywords and not config.getoption("--integration", default=False):
            item.add_marker(skip_integration)

        # Skip slow tests unless --slow flag is passed
        if "slow" in item.keywords and not config.getoption("--slow", default=False):
            item.add_marker(skip_slow)

        # Skip tests requiring API keys if keys are not set
        if "requires_api_key" in item.keywords:
            # Check if any API key is available
            has_api_key = any([
                os.getenv("OPENAI_APIKEY"),
                os.getenv("ANTHROPIC_APIKEY"),
                os.getenv("GROQ_APIKEY"),
            ])
            if not has_api_key:
                item.add_marker(skip_requires_api)


def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests"
    )
    parser.addoption(
        "--slow",
        action="store_true",
        default=False,
        help="run slow tests"
    )
    parser.addoption(
        "--benchmark",
        action="store_true",
        default=False,
        help="run performance benchmarks"
    )
