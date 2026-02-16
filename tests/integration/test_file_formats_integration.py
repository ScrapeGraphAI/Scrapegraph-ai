"""
Integration tests for different file format scrapers.

Tests for:
- JSONScraperGraph
- XMLScraperGraph
- CSVScraperGraph
"""

import pytest

from scrapegraphai.graphs import (
    CSVScraperGraph,
    JSONScraperGraph,
    XMLScraperGraph,
)
from tests.fixtures.helpers import assert_valid_scrape_result


@pytest.mark.integration
@pytest.mark.requires_api_key
class TestJSONScraperIntegration:
    """Integration tests for JSONScraperGraph."""

    def test_scrape_json_file(self, openai_config, temp_json_file):
        """Test scraping a JSON file."""
        scraper = JSONScraperGraph(
            prompt="What is the company name and location?",
            source=temp_json_file,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)

    def test_scrape_json_url(self, openai_config, mock_server):
        """Test scraping JSON from a URL."""
        url = mock_server.get_url("/api/data.json")

        scraper = JSONScraperGraph(
            prompt="List all employees and their roles",
            source=url,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)


@pytest.mark.integration
@pytest.mark.requires_api_key
class TestXMLScraperIntegration:
    """Integration tests for XMLScraperGraph."""

    def test_scrape_xml_file(self, openai_config, temp_xml_file):
        """Test scraping an XML file."""
        scraper = XMLScraperGraph(
            prompt="What employees are listed?",
            source=temp_xml_file,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)

    def test_scrape_xml_url(self, openai_config, mock_server):
        """Test scraping XML from a URL."""
        url = mock_server.get_url("/api/data.xml")

        scraper = XMLScraperGraph(
            prompt="What is the company name?",
            source=url,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)


@pytest.mark.integration
@pytest.mark.requires_api_key
class TestCSVScraperIntegration:
    """Integration tests for CSVScraperGraph."""

    def test_scrape_csv_file(self, openai_config, temp_csv_file):
        """Test scraping a CSV file."""
        scraper = CSVScraperGraph(
            prompt="How many people work in Engineering?",
            source=temp_csv_file,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)

    def test_scrape_csv_url(self, openai_config, mock_server):
        """Test scraping CSV from a URL."""
        url = mock_server.get_url("/api/data.csv")

        scraper = CSVScraperGraph(
            prompt="List all departments",
            source=url,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)


@pytest.mark.integration
@pytest.mark.benchmark
class TestFileFormatPerformance:
    """Performance benchmarks for file format scrapers."""

    @pytest.mark.requires_api_key
    def test_json_scraping_performance(
        self, openai_config, temp_json_file, benchmark_tracker
    ):
        """Benchmark JSON scraping performance."""
        import time

        start_time = time.perf_counter()

        scraper = JSONScraperGraph(
            prompt="Summarize the data",
            source=temp_json_file,
            config=openai_config,
        )

        result = scraper.run()
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        from tests.fixtures.benchmarking import BenchmarkResult

        benchmark_result = BenchmarkResult(
            test_name="json_scraper_performance",
            execution_time=execution_time,
            success=result is not None,
        )

        benchmark_tracker.record(benchmark_result)

        assert_valid_scrape_result(result)
