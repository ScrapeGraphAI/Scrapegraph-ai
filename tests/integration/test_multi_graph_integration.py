"""
Integration tests for multi-page scraping graphs.

Tests for:
- SmartScraperMultiGraph
- SearchGraph
- Other multi-page scrapers
"""

import pytest

from scrapegraphai.graphs import SmartScraperMultiGraph
from tests.fixtures.helpers import assert_valid_scrape_result


@pytest.mark.integration
@pytest.mark.requires_api_key
class TestMultiGraphIntegration:
    """Integration tests for multi-page scraping."""

    def test_scrape_multiple_pages(self, openai_config, mock_server):
        """Test scraping multiple pages simultaneously."""
        urls = [
            mock_server.get_url("/projects"),
            mock_server.get_url("/products"),
        ]

        scraper = SmartScraperMultiGraph(
            prompt="List all items from each page",
            source=urls,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)
        assert isinstance(result, (list, dict))

    def test_concurrent_scraping_performance(
        self, openai_config, mock_server, benchmark_tracker
    ):
        """Test performance of concurrent scraping."""
        import time

        urls = [
            mock_server.get_url("/projects"),
            mock_server.get_url("/products"),
            mock_server.get_url("/"),
        ]

        start_time = time.perf_counter()

        scraper = SmartScraperMultiGraph(
            prompt="Extract main content from each page",
            source=urls,
            config=openai_config,
        )

        result = scraper.run()
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Record benchmark
        from tests.fixtures.benchmarking import BenchmarkResult

        benchmark_result = BenchmarkResult(
            test_name="multi_graph_concurrent",
            execution_time=execution_time,
            success=result is not None,
        )

        benchmark_tracker.record(benchmark_result)

        assert_valid_scrape_result(result)


@pytest.mark.integration
@pytest.mark.slow
class TestSearchGraphIntegration:
    """Integration tests for SearchGraph."""

    @pytest.mark.requires_api_key
    @pytest.mark.skip(reason="Requires internet access and search API")
    def test_search_and_scrape(self, openai_config):
        """Test searching and scraping results."""
        from scrapegraphai.graphs import SearchGraph

        scraper = SearchGraph(
            prompt="What is ScrapeGraphAI?",
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)
