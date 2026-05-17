"""
Tests for the OpenAI Batch API integration.

Tests cover:
- batch_api.py utility functions
- BatchGenerateAnswerNode
- SmartScraperMultiBatchGraph initialization and validation
"""

import json

import pytest

from scrapegraphai.utils.batch_api import (
    BatchJobInfo,
    BatchRequest,
    BatchResult,
    retrieve_batch_results,
)


# ─── BatchRequest Tests ───


class TestBatchRequest:
    """Tests for the BatchRequest dataclass."""

    def test_to_jsonl_line_basic(self):
        """Test basic JSONL line generation."""
        req = BatchRequest(
            custom_id="doc_0000",
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
        )
        line = req.to_jsonl_line()
        data = json.loads(line)

        assert data["custom_id"] == "doc_0000"
        assert data["method"] == "POST"
        assert data["url"] == "/v1/chat/completions"
        assert data["body"]["model"] == "gpt-4o-mini"
        assert data["body"]["messages"] == [{"role": "user", "content": "Hello"}]
        assert data["body"]["temperature"] == 0.0

    def test_to_jsonl_line_with_max_tokens(self):
        """Test JSONL line with max_tokens specified."""
        req = BatchRequest(
            custom_id="doc_0001",
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=500,
        )
        data = json.loads(req.to_jsonl_line())
        assert data["body"]["max_tokens"] == 500

    def test_to_jsonl_line_with_response_format(self):
        """Test JSONL line with response_format specified."""
        req = BatchRequest(
            custom_id="doc_0002",
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Extract"}],
            response_format={"type": "json_object"},
        )
        data = json.loads(req.to_jsonl_line())
        assert data["body"]["response_format"] == {"type": "json_object"}

    def test_to_jsonl_line_without_optional_fields(self):
        """Test that optional fields are excluded when None."""
        req = BatchRequest(
            custom_id="doc_0003",
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test"}],
        )
        data = json.loads(req.to_jsonl_line())
        assert "max_tokens" not in data["body"]
        assert "response_format" not in data["body"]

    def test_to_jsonl_line_custom_temperature(self):
        """Test custom temperature in JSONL output."""
        req = BatchRequest(
            custom_id="doc_0004",
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test"}],
            temperature=0.7,
        )
        data = json.loads(req.to_jsonl_line())
        assert data["body"]["temperature"] == 0.7


# ─── BatchResult Tests ───


class TestBatchResult:
    """Tests for the BatchResult dataclass."""

    def test_successful_result(self):
        """Test creating a successful batch result."""
        result = BatchResult(
            custom_id="doc_0000",
            content='{"key": "value"}',
            usage={"prompt_tokens": 100, "completion_tokens": 50},
        )
        assert result.custom_id == "doc_0000"
        assert result.content == '{"key": "value"}'
        assert result.error is None
        assert result.usage["prompt_tokens"] == 100

    def test_failed_result(self):
        """Test creating a failed batch result."""
        result = BatchResult(
            custom_id="doc_0001",
            error="Rate limit exceeded",
        )
        assert result.custom_id == "doc_0001"
        assert result.content is None
        assert result.error == "Rate limit exceeded"


# ─── BatchJobInfo Tests ───


class TestBatchJobInfo:
    """Tests for the BatchJobInfo dataclass."""

    def test_completed_batch(self):
        """Test a completed batch job info."""
        info = BatchJobInfo(
            batch_id="batch_123",
            status="completed",
            total_requests=10,
            completed_requests=10,
            failed_requests=0,
            output_file_id="file-abc",
        )
        assert info.status == "completed"
        assert info.total_requests == 10
        assert info.failed_requests == 0

    def test_in_progress_batch(self):
        """Test an in-progress batch job info."""
        info = BatchJobInfo(
            batch_id="batch_456",
            status="in_progress",
            total_requests=100,
            completed_requests=42,
            failed_requests=1,
        )
        assert info.status == "in_progress"
        assert info.completed_requests == 42
        assert info.output_file_id is None


# ─── retrieve_batch_results Tests ───


class TestRetrieveBatchResults:
    """Tests for result retrieval and parsing."""

    def test_retrieve_no_output_file(self):
        """Test that retrieval fails when no output file is available."""
        info = BatchJobInfo(
            batch_id="batch_789",
            status="failed",
            output_file_id=None,
        )

        class DummyClient:
            pass

        with pytest.raises(ValueError, match="no output file"):
            retrieve_batch_results(DummyClient(), info)

    def test_results_sorted_by_custom_id(self):
        """Test that results are sorted by custom_id for consistent ordering."""
        # Simulate results out of order
        jsonl_output = "\n".join([
            json.dumps({
                "custom_id": "doc_0002",
                "response": {
                    "body": {
                        "choices": [{"message": {"content": '{"val": "c"}'}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                    }
                },
            }),
            json.dumps({
                "custom_id": "doc_0000",
                "response": {
                    "body": {
                        "choices": [{"message": {"content": '{"val": "a"}'}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                    }
                },
            }),
            json.dumps({
                "custom_id": "doc_0001",
                "response": {
                    "body": {
                        "choices": [{"message": {"content": '{"val": "b"}'}}],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                    }
                },
            }),
        ])

        class DummyFileContent:
            text = jsonl_output

        class DummyFiles:
            def content(self, file_id):
                return DummyFileContent()

        class DummyClient:
            files = DummyFiles()

        info = BatchJobInfo(
            batch_id="batch_sorted",
            status="completed",
            output_file_id="file-sorted",
        )

        results = retrieve_batch_results(DummyClient(), info)

        assert len(results) == 3
        assert results[0].custom_id == "doc_0000"
        assert results[1].custom_id == "doc_0001"
        assert results[2].custom_id == "doc_0002"
        assert results[0].content == '{"val": "a"}'

    def test_handles_partial_failures(self):
        """Test that partial failures in batch results are handled correctly."""
        jsonl_output = "\n".join([
            json.dumps({
                "custom_id": "doc_0000",
                "response": {
                    "body": {
                        "choices": [{"message": {"content": '{"result": "ok"}'}}],
                    }
                },
            }),
            json.dumps({
                "custom_id": "doc_0001",
                "error": {"code": "rate_limit", "message": "Too many requests"},
            }),
        ])

        class DummyFileContent:
            text = jsonl_output

        class DummyFiles:
            def content(self, file_id):
                return DummyFileContent()

        class DummyClient:
            files = DummyFiles()

        info = BatchJobInfo(
            batch_id="batch_partial",
            status="completed",
            output_file_id="file-partial",
        )

        results = retrieve_batch_results(DummyClient(), info)

        assert len(results) == 2
        # doc_0000 succeeded
        assert results[0].content == '{"result": "ok"}'
        assert results[0].error is None
        # doc_0001 failed
        assert results[1].error is not None
        assert results[1].content is None


# ─── SmartScraperMultiBatchGraph Validation Tests ───


class TestSmartScraperMultiBatchGraphValidation:
    """Tests for SmartScraperMultiBatchGraph initialization validation."""

    def test_rejects_non_openai_provider(self):
        """Test that non-OpenAI providers are rejected."""
        from scrapegraphai.graphs.smart_scraper_multi_batch_graph import (
            SmartScraperMultiBatchGraph,
        )

        with pytest.raises(ValueError, match="only supports OpenAI"):
            SmartScraperMultiBatchGraph(
                prompt="Test prompt",
                source=["https://example.com"],
                config={"llm": {"model": "anthropic/claude-3"}},
            )

    def test_rejects_groq_provider(self):
        """Test that Groq provider is rejected."""
        from scrapegraphai.graphs.smart_scraper_multi_batch_graph import (
            SmartScraperMultiBatchGraph,
        )

        with pytest.raises(ValueError, match="only supports OpenAI"):
            SmartScraperMultiBatchGraph(
                prompt="Test",
                source=["https://example.com"],
                config={"llm": {"model": "groq/llama-3"}},
            )


# ─── BatchGenerateAnswerNode Tests ───


class TestBatchGenerateAnswerNode:
    """Tests for the BatchGenerateAnswerNode."""

    def test_empty_parsed_docs_raises(self):
        """Test that empty parsed_docs raises ValueError."""
        from scrapegraphai.nodes.batch_generate_answer_node import (
            BatchGenerateAnswerNode,
        )

        class DummyLLM:
            model_name = "gpt-4o-mini"

        node = BatchGenerateAnswerNode(
            input="user_prompt & parsed_docs",
            output=["results"],
            node_config={
                "llm_model": DummyLLM(),
                "batch_config": {},
            },
        )

        class DummyLogger:
            def info(self, msg):
                pass
            def error(self, msg):
                pass
            def warning(self, msg):
                pass

        node.logger = DummyLogger()
        node.get_input_keys = lambda state: ["user_prompt", "parsed_docs"]

        with pytest.raises(ValueError, match="No parsed documents"):
            node.execute({
                "user_prompt": "Test",
                "parsed_docs": [],
                "urls": [],
            })

    def test_model_name_extraction(self):
        """Test model name is correctly extracted from LLM instance."""
        from scrapegraphai.nodes.batch_generate_answer_node import (
            BatchGenerateAnswerNode,
        )

        class DummyLLM:
            model_name = "gpt-4o-mini"

        node = BatchGenerateAnswerNode(
            input="user_prompt & parsed_docs",
            output=["results"],
            node_config={"llm_model": DummyLLM(), "batch_config": {}},
        )

        assert node._get_model_name() == "gpt-4o-mini"

    def test_batch_model_override(self):
        """Test that batch_config model overrides the LLM model name."""
        from scrapegraphai.nodes.batch_generate_answer_node import (
            BatchGenerateAnswerNode,
        )

        class DummyLLM:
            model_name = "gpt-4o-mini"

        node = BatchGenerateAnswerNode(
            input="user_prompt & parsed_docs",
            output=["results"],
            node_config={
                "llm_model": DummyLLM(),
                "batch_config": {"model": "gpt-4o"},
            },
        )

        assert node._get_model_name() == "gpt-4o"

    def test_format_instructions_without_schema(self):
        """Test default format instructions when no schema is provided."""
        from scrapegraphai.nodes.batch_generate_answer_node import (
            BatchGenerateAnswerNode,
        )

        class DummyLLM:
            model_name = "gpt-4o-mini"

        node = BatchGenerateAnswerNode(
            input="user_prompt & parsed_docs",
            output=["results"],
            node_config={"llm_model": DummyLLM(), "batch_config": {}},
        )

        instructions = node._get_format_instructions()
        assert "JSON" in instructions
        assert "content" in instructions
