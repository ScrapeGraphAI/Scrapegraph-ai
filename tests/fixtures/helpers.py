"""
Test utilities and helpers for ScrapeGraphAI tests.

This module provides:
- Assertion helpers
- Data validation utilities
- Mock response builders
- Test data generators
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock


# ============================================================================
# Assertion Helpers
# ============================================================================


def assert_valid_scrape_result(result: Any, expected_keys: Optional[List[str]] = None):
    """Assert that a scraping result is valid.

    Args:
        result: The scraping result to validate
        expected_keys: Optional list of keys that should be present
    """
    assert result is not None, "Result should not be None"
    assert isinstance(result, (dict, str)), f"Result should be dict or str, got {type(result)}"

    if isinstance(result, dict) and expected_keys:
        for key in expected_keys:
            assert key in result, f"Expected key '{key}' not found in result"


def assert_execution_info_valid(exec_info: Dict[str, Any]):
    """Assert that execution info is valid and contains expected fields.

    Args:
        exec_info: Execution info dictionary
    """
    assert exec_info is not None, "Execution info should not be None"
    assert isinstance(exec_info, dict), "Execution info should be a dictionary"


def assert_response_time_acceptable(execution_time: float, max_time: float = 30.0):
    """Assert that response time is within acceptable limits.

    Args:
        execution_time: Actual execution time in seconds
        max_time: Maximum acceptable time in seconds
    """
    assert (
        execution_time <= max_time
    ), f"Execution time {execution_time}s exceeded maximum {max_time}s"


def assert_no_errors_in_result(result: Union[Dict, str]):
    """Assert that the result doesn't contain common error indicators.

    Args:
        result: The result to check
    """
    result_str = json.dumps(result) if isinstance(result, dict) else str(result)
    error_indicators = [
        "error",
        "exception",
        "failed",
        "timeout",
        "rate limit",
    ]

    for indicator in error_indicators:
        assert indicator.lower() not in result_str.lower(), (
            f"Result contains error indicator: {indicator}"
        )


# ============================================================================
# Mock Response Builders
# ============================================================================


def create_mock_llm_response(content: str, **kwargs) -> Mock:
    """Create a mock LLM response.

    Args:
        content: Response content
        **kwargs: Additional response attributes

    Returns:
        Mock response object
    """
    mock = Mock()
    mock.content = content
    mock.response_metadata = kwargs.get("metadata", {})
    mock.__str__ = lambda: content
    return mock


def create_mock_graph_result(
    answer: Any = None,
    exec_info: Optional[Dict] = None,
    error: Optional[str] = None,
) -> tuple:
    """Create a mock graph execution result.

    Args:
        answer: The answer/result
        exec_info: Execution info dictionary
        error: Optional error message

    Returns:
        Tuple of (state, exec_info)
    """
    state = {}
    if answer is not None:
        state["answer"] = answer
    if error:
        state["error"] = error

    info = exec_info or {}

    return (state, info)


# ============================================================================
# Data Generators
# ============================================================================


def generate_test_html(
    title: str = "Test Page",
    num_items: int = 3,
    item_template: str = "Item {n}",
) -> str:
    """Generate test HTML with customizable content.

    Args:
        title: Page title
        num_items: Number of list items to generate
        item_template: Template for item text (use {n} for number)

    Returns:
        HTML string
    """
    items = "\n".join(
        [f"<li>{item_template.format(n=i+1)}</li>" for i in range(num_items)]
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head><title>{title}</title></head>
    <body>
        <h1>{title}</h1>
        <ul>{items}</ul>
    </body>
    </html>
    """


def generate_test_json(num_records: int = 3) -> Dict[str, Any]:
    """Generate test JSON data.

    Args:
        num_records: Number of records to generate

    Returns:
        Dictionary with test data
    """
    return {
        "items": [
            {
                "id": i + 1,
                "name": f"Item {i + 1}",
                "description": f"Description for item {i + 1}",
                "value": (i + 1) * 10,
            }
            for i in range(num_records)
        ],
        "total": num_records,
    }


def generate_test_csv(num_rows: int = 3) -> str:
    """Generate test CSV data.

    Args:
        num_rows: Number of data rows to generate

    Returns:
        CSV string
    """
    header = "id,name,value"
    rows = [f"{i+1},Item {i+1},{(i+1)*10}" for i in range(num_rows)]
    return header + "\n" + "\n".join(rows)


# ============================================================================
# Validation Utilities
# ============================================================================


def validate_schema_match(data: Dict, schema_class) -> bool:
    """Validate that data matches a Pydantic schema.

    Args:
        data: Data to validate
        schema_class: Pydantic schema class

    Returns:
        True if valid, False otherwise
    """
    try:
        schema_class(**data)
        return True
    except Exception:
        return False


def validate_extracted_fields(
    result: Dict, required_fields: List[str], min_values: int = 1
) -> bool:
    """Validate that required fields were extracted with minimum values.

    Args:
        result: Extraction result
        required_fields: List of required field names
        min_values: Minimum number of values per field

    Returns:
        True if validation passes
    """
    for field in required_fields:
        if field not in result:
            return False

        value = result[field]
        if isinstance(value, list) and len(value) < min_values:
            return False

    return True


# ============================================================================
# File Utilities
# ============================================================================


def load_test_fixture(fixture_name: str, fixture_dir: Optional[Path] = None) -> str:
    """Load a test fixture file.

    Args:
        fixture_name: Name of the fixture file
        fixture_dir: Directory containing fixtures (defaults to tests/fixtures)

    Returns:
        File contents as string
    """
    if fixture_dir is None:
        fixture_dir = Path(__file__).parent

    fixture_path = fixture_dir / fixture_name
    return fixture_path.read_text()


def save_test_output(
    content: str, filename: str, output_dir: Optional[Path] = None
):
    """Save test output to a file for debugging.

    Args:
        content: Content to save
        filename: Output filename
        output_dir: Output directory (defaults to tests/output)
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "output"

    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / filename
    output_path.write_text(content)


# ============================================================================
# Comparison Utilities
# ============================================================================


def compare_results(result1: Dict, result2: Dict, ignore_keys: Optional[List[str]] = None) -> bool:
    """Compare two scraping results, optionally ignoring certain keys.

    Args:
        result1: First result
        result2: Second result
        ignore_keys: Keys to ignore in comparison

    Returns:
        True if results match
    """
    ignore_keys = ignore_keys or []

    # Create copies and remove ignored keys
    r1 = {k: v for k, v in result1.items() if k not in ignore_keys}
    r2 = {k: v for k, v in result2.items() if k not in ignore_keys}

    return r1 == r2


def fuzzy_match_strings(str1: str, str2: str, threshold: float = 0.8) -> bool:
    """Check if two strings are similar enough.

    Args:
        str1: First string
        str2: Second string
        threshold: Similarity threshold (0-1)

    Returns:
        True if strings are similar enough
    """
    # Simple implementation using character overlap
    # For production, consider using libraries like difflib or fuzzywuzzy
    set1 = set(str1.lower().split())
    set2 = set(str2.lower().split())

    if not set1 and not set2:
        return True
    if not set1 or not set2:
        return False

    overlap = len(set1.intersection(set2))
    total = len(set1.union(set2))

    similarity = overlap / total if total > 0 else 0
    return similarity >= threshold


# ============================================================================
# Rate Limiting Utilities
# ============================================================================


class RateLimitHelper:
    """Helper for testing rate limiting behavior."""

    def __init__(self, max_requests: int, time_window: float):
        """Initialize rate limit helper.

        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []

    def can_make_request(self) -> bool:
        """Check if a new request can be made.

        Returns:
            True if request is allowed
        """
        import time

        now = time.time()

        # Remove old requests outside the time window
        self.requests = [r for r in self.requests if now - r < self.time_window]

        return len(self.requests) < self.max_requests

    def record_request(self):
        """Record a new request."""
        import time

        self.requests.append(time.time())


# ============================================================================
# Retry Utilities
# ============================================================================


def retry_with_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
):
    """Retry a function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay on each retry

    Returns:
        Function result

    Raises:
        Last exception if all retries fail
    """
    import time

    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(delay)
                delay *= backoff_factor
            else:
                raise last_exception
