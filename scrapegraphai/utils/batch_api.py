"""
OpenAI Batch API utility functions.

Provides helpers for creating, polling, and retrieving results
from the OpenAI Batch API, enabling 50% cost savings on LLM calls
when real-time responses are not needed.

Reference: https://platform.openai.com/docs/guides/batch
"""

import io
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

# OpenAI Batch API limits
MAX_REQUESTS_PER_BATCH = 50_000
DEFAULT_POLL_INTERVAL = 30  # seconds
DEFAULT_MAX_WAIT_TIME = 86_400  # 24 hours


@dataclass
class BatchRequest:
    """A single request within a batch submission."""

    custom_id: str
    """Unique identifier for mapping responses back to requests."""

    model: str
    """The OpenAI model to use (e.g., 'gpt-4o-mini')."""

    messages: List[Dict[str, str]]
    """The chat messages for this request."""

    temperature: float = 0.0
    """Sampling temperature."""

    max_tokens: Optional[int] = None
    """Maximum tokens in the response."""

    response_format: Optional[Dict[str, str]] = None
    """Optional response format (e.g., {"type": "json_object"})."""

    def to_jsonl_line(self) -> str:
        """Convert to a JSONL line for the Batch API input file."""
        body = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
        }
        if self.max_tokens is not None:
            body["max_tokens"] = self.max_tokens
        if self.response_format is not None:
            body["response_format"] = self.response_format

        return json.dumps({
            "custom_id": self.custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": body,
        })


@dataclass
class BatchResult:
    """The result of a single request within a completed batch."""

    custom_id: str
    """The custom ID that was provided in the request."""

    content: Optional[str] = None
    """The response content from the LLM."""

    error: Optional[str] = None
    """Error message if this individual request failed."""

    usage: Optional[Dict[str, int]] = None
    """Token usage for this request."""


@dataclass
class BatchJobInfo:
    """Status information about a batch job."""

    batch_id: str
    """The OpenAI batch ID."""

    status: str
    """Current status: validating, in_progress, completed, failed, expired, etc."""

    total_requests: int = 0
    """Total number of requests in the batch."""

    completed_requests: int = 0
    """Number of completed requests."""

    failed_requests: int = 0
    """Number of failed requests."""

    output_file_id: Optional[str] = None
    """ID of the output file when batch completes."""

    error_file_id: Optional[str] = None
    """ID of the error file if there are errors."""


def create_batch(
    client: OpenAI,
    requests: List[BatchRequest],
    description: str = "ScrapeGraphAI batch scraping job",
) -> str:
    """Create and submit an OpenAI Batch API job.

    Args:
        client: An initialized OpenAI client.
        requests: List of BatchRequest objects to submit.
        description: Human-readable description for the batch.

    Returns:
        The batch ID for tracking the job.

    Raises:
        ValueError: If the number of requests exceeds the API limit.
    """
    if len(requests) > MAX_REQUESTS_PER_BATCH:
        raise ValueError(
            f"Batch size {len(requests)} exceeds the maximum of "
            f"{MAX_REQUESTS_PER_BATCH}. Split into multiple batches."
        )

    # Build JSONL content
    jsonl_content = "\n".join(req.to_jsonl_line() for req in requests)

    logger.info(
        f"Uploading batch input file with {len(requests)} requests..."
    )

    # Upload the input file
    input_file = client.files.create(
        file=io.BytesIO(jsonl_content.encode("utf-8")),
        purpose="batch",
    )

    logger.info(f"Input file uploaded: {input_file.id}")

    # Create the batch
    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={"description": description},
    )

    logger.info(
        f"Batch created: {batch.id} (status: {batch.status})"
    )

    return batch.id


def get_batch_status(client: OpenAI, batch_id: str) -> BatchJobInfo:
    """Get the current status of a batch job.

    Args:
        client: An initialized OpenAI client.
        batch_id: The batch ID returned by create_batch.

    Returns:
        BatchJobInfo with the current status and counts.
    """
    batch = client.batches.retrieve(batch_id)

    return BatchJobInfo(
        batch_id=batch.id,
        status=batch.status,
        total_requests=batch.request_counts.total if batch.request_counts else 0,
        completed_requests=batch.request_counts.completed if batch.request_counts else 0,
        failed_requests=batch.request_counts.failed if batch.request_counts else 0,
        output_file_id=batch.output_file_id,
        error_file_id=batch.error_file_id,
    )


def poll_batch_until_complete(
    client: OpenAI,
    batch_id: str,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    max_wait_time: int = DEFAULT_MAX_WAIT_TIME,
) -> BatchJobInfo:
    """Poll a batch job until it completes, fails, or times out.

    Args:
        client: An initialized OpenAI client.
        batch_id: The batch ID to poll.
        poll_interval: Seconds between status checks.
        max_wait_time: Maximum seconds to wait before giving up.

    Returns:
        Final BatchJobInfo when the batch reaches a terminal state.

    Raises:
        TimeoutError: If max_wait_time is exceeded.
        RuntimeError: If the batch fails or is cancelled.
    """
    terminal_states = {"completed", "failed", "expired", "cancelled"}
    start_time = time.time()

    logger.info(
        f"Polling batch {batch_id} every {poll_interval}s "
        f"(max wait: {max_wait_time}s)..."
    )

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait_time:
            raise TimeoutError(
                f"Batch {batch_id} did not complete within "
                f"{max_wait_time}s (last status check at {elapsed:.0f}s)"
            )

        info = get_batch_status(client, batch_id)

        logger.info(
            f"Batch {batch_id}: {info.status} "
            f"({info.completed_requests}/{info.total_requests} done, "
            f"{info.failed_requests} failed)"
        )

        if info.status in terminal_states:
            if info.status == "failed":
                raise RuntimeError(
                    f"Batch {batch_id} failed. "
                    f"Error file: {info.error_file_id}"
                )
            if info.status in {"expired", "cancelled"}:
                raise RuntimeError(
                    f"Batch {batch_id} was {info.status}."
                )
            return info

        time.sleep(poll_interval)


def retrieve_batch_results(
    client: OpenAI,
    batch_info: BatchJobInfo,
) -> List[BatchResult]:
    """Retrieve and parse results from a completed batch.

    Args:
        client: An initialized OpenAI client.
        batch_info: A BatchJobInfo from a completed batch.

    Returns:
        List of BatchResult objects, one per request,
        ordered by their custom_id.
    """
    if not batch_info.output_file_id:
        raise ValueError(
            f"Batch {batch_info.batch_id} has no output file. "
            f"Status: {batch_info.status}"
        )

    logger.info(f"Downloading results from {batch_info.output_file_id}...")

    output_content = client.files.content(batch_info.output_file_id).text
    results = []

    for line in output_content.strip().split("\n"):
        if not line:
            continue

        response_data = json.loads(line)
        custom_id = response_data["custom_id"]

        error = response_data.get("error")
        if error:
            results.append(BatchResult(
                custom_id=custom_id,
                error=json.dumps(error),
            ))
            continue

        body = response_data.get("response", {}).get("body", {})
        choices = body.get("choices", [])

        if choices:
            content = choices[0].get("message", {}).get("content", "")
            usage = body.get("usage")
            results.append(BatchResult(
                custom_id=custom_id,
                content=content,
                usage=usage,
            ))
        else:
            results.append(BatchResult(
                custom_id=custom_id,
                error="No choices returned in response",
            ))

    # Sort by custom_id to maintain order
    results.sort(key=lambda r: r.custom_id)

    logger.info(
        f"Retrieved {len(results)} results "
        f"({sum(1 for r in results if r.error is None)} succeeded, "
        f"{sum(1 for r in results if r.error is not None)} failed)"
    )

    return results
