"""
Performance benchmarking framework for ScrapeGraphAI.

This module provides utilities for:
- Measuring execution time
- Tracking token usage
- Monitoring API calls
- Generating performance reports
- Comparing performance across runs
"""

import json
import statistics
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import pytest


@dataclass
class BenchmarkResult:
    """Results from a single benchmark run."""

    test_name: str
    execution_time: float
    memory_usage: Optional[float] = None
    token_usage: Optional[int] = None
    api_calls: int = 0
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkSummary:
    """Summary statistics for multiple benchmark runs."""

    test_name: str
    num_runs: int
    mean_time: float
    median_time: float
    std_dev: float
    min_time: float
    max_time: float
    success_rate: float
    total_tokens: Optional[int] = None
    total_api_calls: int = 0


class BenchmarkTracker:
    """Track and analyze benchmark results."""

    def __init__(self, output_dir: Optional[Path] = None):
        """Initialize the benchmark tracker.

        Args:
            output_dir: Directory to save benchmark results
        """
        self.output_dir = output_dir or Path("benchmark_results")
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[BenchmarkResult] = []

    def record(self, result: BenchmarkResult):
        """Record a benchmark result."""
        self.results.append(result)

    def get_summary(self, test_name: str) -> Optional[BenchmarkSummary]:
        """Get summary statistics for a specific test.

        Args:
            test_name: Name of the test

        Returns:
            BenchmarkSummary if results exist, None otherwise
        """
        test_results = [r for r in self.results if r.test_name == test_name]
        if not test_results:
            return None

        times = [r.execution_time for r in test_results]
        successes = [r.success for r in test_results]
        tokens = [r.token_usage for r in test_results if r.token_usage is not None]
        api_calls = sum(r.api_calls for r in test_results)

        return BenchmarkSummary(
            test_name=test_name,
            num_runs=len(test_results),
            mean_time=statistics.mean(times),
            median_time=statistics.median(times),
            std_dev=statistics.stdev(times) if len(times) > 1 else 0.0,
            min_time=min(times),
            max_time=max(times),
            success_rate=sum(successes) / len(successes),
            total_tokens=sum(tokens) if tokens else None,
            total_api_calls=api_calls,
        )

    def save_results(self, filename: str = "benchmark_results.json"):
        """Save all benchmark results to a JSON file.

        Args:
            filename: Name of the output file
        """
        filepath = self.output_dir / filename
        data = {
            "results": [
                {
                    "test_name": r.test_name,
                    "execution_time": r.execution_time,
                    "memory_usage": r.memory_usage,
                    "token_usage": r.token_usage,
                    "api_calls": r.api_calls,
                    "success": r.success,
                    "error": r.error,
                    "metadata": r.metadata,
                }
                for r in self.results
            ]
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def generate_report(self) -> str:
        """Generate a human-readable performance report.

        Returns:
            Formatted report string
        """
        if not self.results:
            return "No benchmark results available."

        # Get unique test names
        test_names = list({r.test_name for r in self.results})

        report = ["=" * 80, "Performance Benchmark Report", "=" * 80, ""]

        for test_name in sorted(test_names):
            summary = self.get_summary(test_name)
            if not summary:
                continue

            report.append(f"\n{test_name}")
            report.append("-" * 80)
            report.append(f"  Runs:          {summary.num_runs}")
            report.append(f"  Mean Time:     {summary.mean_time:.4f}s")
            report.append(f"  Median Time:   {summary.median_time:.4f}s")
            report.append(f"  Std Dev:       {summary.std_dev:.4f}s")
            report.append(f"  Min Time:      {summary.min_time:.4f}s")
            report.append(f"  Max Time:      {summary.max_time:.4f}s")
            report.append(f"  Success Rate:  {summary.success_rate * 100:.1f}%")
            if summary.total_tokens:
                report.append(f"  Total Tokens:  {summary.total_tokens}")
            if summary.total_api_calls:
                report.append(f"  API Calls:     {summary.total_api_calls}")

        report.append("\n" + "=" * 80)
        return "\n".join(report)


def benchmark(
    func: Callable,
    name: Optional[str] = None,
    warmup_runs: int = 1,
    test_runs: int = 3,
    tracker: Optional[BenchmarkTracker] = None,
) -> BenchmarkSummary:
    """Benchmark a function with multiple runs.

    Args:
        func: Function to benchmark
        name: Name for the benchmark (defaults to function name)
        warmup_runs: Number of warmup runs to discard
        test_runs: Number of actual test runs to measure
        tracker: Optional BenchmarkTracker to record results

    Returns:
        BenchmarkSummary with statistics
    """
    test_name = name or func.__name__
    local_tracker = tracker or BenchmarkTracker()

    # Warmup runs
    for _ in range(warmup_runs):
        try:
            func()
        except Exception:
            pass

    # Test runs
    for run in range(test_runs):
        start_time = time.perf_counter()
        success = True
        error = None

        try:
            result = func()
            # Try to extract metadata if result is dict-like
            metadata = {}
            if isinstance(result, dict):
                metadata = result.get("metadata", {})
        except Exception as e:
            success = False
            error = str(e)
            metadata = {}

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        benchmark_result = BenchmarkResult(
            test_name=test_name,
            execution_time=execution_time,
            success=success,
            error=error,
            metadata=metadata,
        )

        local_tracker.record(benchmark_result)

    return local_tracker.get_summary(test_name)


@pytest.fixture
def benchmark_tracker():
    """Pytest fixture for benchmark tracking."""
    tracker = BenchmarkTracker()
    yield tracker
    # Save results after test completes
    tracker.save_results()


def pytest_benchmark_compare(baseline_file: Path, current_file: Path) -> Dict[str, Any]:
    """Compare current benchmark results against a baseline.

    Args:
        baseline_file: Path to baseline results JSON
        current_file: Path to current results JSON

    Returns:
        Dictionary with comparison results
    """
    with open(baseline_file) as f:
        baseline = json.load(f)

    with open(current_file) as f:
        current = json.load(f)

    # Create lookup for baseline results
    baseline_by_name = {r["test_name"]: r for r in baseline["results"]}

    comparison = {"regressions": [], "improvements": [], "new_tests": []}

    for current_result in current["results"]:
        test_name = current_result["test_name"]

        if test_name not in baseline_by_name:
            comparison["new_tests"].append(test_name)
            continue

        baseline_result = baseline_by_name[test_name]
        current_time = current_result["execution_time"]
        baseline_time = baseline_result["execution_time"]

        # Calculate percentage change
        change_pct = ((current_time - baseline_time) / baseline_time) * 100

        # Threshold for regression (e.g., 10% slower)
        regression_threshold = 10.0

        if change_pct > regression_threshold:
            comparison["regressions"].append(
                {
                    "test_name": test_name,
                    "baseline_time": baseline_time,
                    "current_time": current_time,
                    "change_pct": change_pct,
                }
            )
        elif change_pct < -regression_threshold:
            comparison["improvements"].append(
                {
                    "test_name": test_name,
                    "baseline_time": baseline_time,
                    "current_time": current_time,
                    "change_pct": change_pct,
                }
            )

    return comparison
