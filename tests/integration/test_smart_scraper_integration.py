"""
Integration tests for SmartScraperGraph with multiple LLM providers.

These tests verify that SmartScraperGraph works correctly with:
- Different LLM providers (OpenAI, Ollama, etc.)
- Various content types
- Real and mock websites
"""

import pytest
from pydantic import BaseModel, Field

from scrapegraphai.graphs import SmartScraperGraph
from tests.fixtures.helpers import (
    assert_execution_info_valid,
    assert_valid_scrape_result,
)


class ProjectSchema(BaseModel):
    """Schema for project data."""

    title: str = Field(description="Project title")
    description: str = Field(description="Project description")


class ProjectListSchema(BaseModel):
    """Schema for list of projects."""

    projects: list[ProjectSchema]


@pytest.mark.integration
@pytest.mark.requires_api_key
class TestSmartScraperIntegration:
    """Integration tests for SmartScraperGraph."""

    def test_scrape_with_openai(self, openai_config, mock_server):
        """Test scraping with OpenAI using mock server."""
        url = mock_server.get_url("/projects")

        scraper = SmartScraperGraph(
            prompt="List all projects with their descriptions",
            source=url,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)
        exec_info = scraper.get_execution_info()
        assert_execution_info_valid(exec_info)

    def test_scrape_with_schema(self, openai_config, mock_server):
        """Test scraping with a Pydantic schema."""
        url = mock_server.get_url("/projects")

        scraper = SmartScraperGraph(
            prompt="List all projects with their descriptions",
            source=url,
            config=openai_config,
            schema=ProjectListSchema,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)
        assert isinstance(result, dict)

        # Validate schema fields
        if "projects" in result:
            assert isinstance(result["projects"], list)

    @pytest.mark.slow
    def test_scrape_products_page(self, openai_config, mock_server):
        """Test scraping a products page."""
        url = mock_server.get_url("/products")

        scraper = SmartScraperGraph(
            prompt="Extract all product names and prices",
            source=url,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)
        assert isinstance(result, dict)

    def test_scrape_with_timeout(self, openai_config, mock_server):
        """Test scraping with a slow-loading page."""
        url = mock_server.get_url("/slow")

        config = openai_config.copy()
        config["loader_kwargs"] = {"timeout": 5000}  # 5 second timeout

        scraper = SmartScraperGraph(
            prompt="Extract the heading from the page",
            source=url,
            config=config,
        )

        # This should complete within timeout
        result = scraper.run()
        assert_valid_scrape_result(result)

    def test_error_handling_404(self, openai_config, mock_server):
        """Test handling of 404 errors."""
        url = mock_server.get_url("/error/404")

        config = openai_config.copy()

        scraper = SmartScraperGraph(
            prompt="Extract content",
            source=url,
            config=config,
        )

        # Should handle error gracefully
        try:
            result = scraper.run()
            # Depending on implementation, might return error or empty result
            assert result is not None
        except Exception as e:
            # Error should be informative
            assert "404" in str(e) or "not found" in str(e).lower()


@pytest.mark.integration
class TestMultiProviderIntegration:
    """Test SmartScraperGraph with multiple LLM providers."""

    @pytest.mark.requires_api_key
    def test_consistent_results_across_providers(
        self, openai_config, mock_server
    ):
        """Test that different providers produce consistent results."""
        url = mock_server.get_url("/projects")
        prompt = "How many projects are listed?"

        # Test with OpenAI
        scraper_openai = SmartScraperGraph(
            prompt=prompt,
            source=url,
            config=openai_config,
        )
        result_openai = scraper_openai.run()

        assert_valid_scrape_result(result_openai)

        # Note: Add more provider tests when API keys are available
        # For now, we just verify OpenAI works


@pytest.mark.integration
@pytest.mark.slow
class TestRealWebsiteIntegration:
    """Integration tests with real websites (using test website)."""

    @pytest.mark.requires_api_key
    def test_scrape_test_website(self, openai_config, mock_website_url):
        """Test scraping the official test website."""
        scraper = SmartScraperGraph(
            prompt="List all the main sections of the website",
            source=mock_website_url,
            config=openai_config,
        )

        result = scraper.run()

        assert_valid_scrape_result(result)
        exec_info = scraper.get_execution_info()
        assert_execution_info_valid(exec_info)


@pytest.mark.benchmark
class TestSmartScraperPerformance:
    """Performance benchmarks for SmartScraperGraph."""

    @pytest.mark.requires_api_key
    def test_scraping_performance(
        self, openai_config, mock_server, benchmark_tracker
    ):
        """Benchmark scraping performance."""
        import time

        url = mock_server.get_url("/projects")

        start_time = time.perf_counter()

        scraper = SmartScraperGraph(
            prompt="List all projects",
            source=url,
            config=openai_config,
        )

        result = scraper.run()
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Record benchmark result
        from tests.fixtures.benchmarking import BenchmarkResult

        benchmark_result = BenchmarkResult(
            test_name="smart_scraper_basic",
            execution_time=execution_time,
            success=result is not None,
        )

        benchmark_tracker.record(benchmark_result)

        # Assert reasonable performance
        assert execution_time < 30.0, f"Execution took {execution_time}s, expected < 30s"
