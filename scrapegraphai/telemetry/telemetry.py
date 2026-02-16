"""
This module contains code that relates to sending ScrapeGraphAI usage telemetry.

To disable sending telemetry there are three ways:

1. Set it to false programmatically in your driver:
  >>> from scrapegraphai import telemetry
  >>> telemetry.disable_telemetry()
2. Set it to `false` in ~/.scrapegraphai.conf under `DEFAULT`
  [DEFAULT]
  telemetry_enabled = False
3. Set SCRAPEGRAPHAI_TELEMETRY_ENABLED=false as an environment variable:
  SCRAPEGRAPHAI_TELEMETRY_ENABLED=false python run.py
  or:
  export SCRAPEGRAPHAI_TELEMETRY_ENABLED=false
"""

import configparser
import importlib.metadata
import json
import logging
import os
import threading
import uuid
from typing import Any, Callable
from urllib import request
from urllib.error import HTTPError, URLError

from pydantic import BaseModel, Field, ValidationError

VERSION = importlib.metadata.version("scrapegraphai")
TRACK_URL = "https://sgai-oss-tracing.onrender.com/v1/telemetry"
TIMEOUT = 2
DEFAULT_CONFIG_LOCATION = os.path.expanduser("~/.scrapegraphai.conf")

logger = logging.getLogger(__name__)


def _load_config(config_location: str) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    try:
        with open(config_location) as f:
            config.read_file(f)
    except (OSError, configparser.Error) as e:
        logger.debug(f"Unable to load config file: {e}")
        config["DEFAULT"] = {}
    else:
        if "DEFAULT" not in config:
            config["DEFAULT"] = {}

    if "anonymous_id" not in config["DEFAULT"]:
        config["DEFAULT"]["anonymous_id"] = str(uuid.uuid4())
        try:
            with open(config_location, "w") as f:
                config.write(f)
        except OSError as e:
            logger.debug(f"Unable to write config file: {e}")
    return config


def _check_config_and_environ_for_telemetry_flag(
    telemetry_default: bool, config_obj: configparser.ConfigParser
) -> bool:
    telemetry_enabled = telemetry_default
    if "telemetry_enabled" in config_obj["DEFAULT"]:
        try:
            telemetry_enabled = config_obj.getboolean("DEFAULT", "telemetry_enabled")
        except ValueError as e:
            logger.debug(
                f"Unable to parse value for `telemetry_enabled` from config. Encountered {e}"
            )
    if os.environ.get("SCRAPEGRAPHAI_TELEMETRY_ENABLED") is not None:
        env_value = os.environ.get("SCRAPEGRAPHAI_TELEMETRY_ENABLED")
        config_obj["DEFAULT"]["telemetry_enabled"] = env_value
        try:
            telemetry_enabled = config_obj.getboolean("DEFAULT", "telemetry_enabled")
        except ValueError as e:
            logger.debug(
                f"Unable to parse value for `SCRAPEGRAPHAI_TELEMETRY_ENABLED` from environment. Encountered {e}"
            )
    return telemetry_enabled


config = _load_config(DEFAULT_CONFIG_LOCATION)
g_telemetry_enabled = _check_config_and_environ_for_telemetry_flag(True, config)
g_anonymous_id = config["DEFAULT"]["anonymous_id"]
CALL_COUNTER = 0
MAX_COUNT_SESSION = 1000


def disable_telemetry():
    """
    function for disabling the telemetries
    """
    global g_telemetry_enabled
    g_telemetry_enabled = False


def is_telemetry_enabled() -> bool:
    """
    function for checking if a telemetry is enables
    """
    if g_telemetry_enabled:
        global CALL_COUNTER
        if CALL_COUNTER == 0:
            logger.debug(
                "Note: ScrapeGraphAI collects anonymous usage data to improve the library. "
                "You can disable telemetry by setting SCRAPEGRAPHAI_TELEMETRY_ENABLED=false or "
                "by editing ~/.scrapegraphai.conf."
            )
        CALL_COUNTER += 1
        if CALL_COUNTER > MAX_COUNT_SESSION:
            return False
        return True
    else:
        return False


class TelemetryEvent(BaseModel):
    """Validated telemetry payload matching the tracing API schema."""

    user_prompt: str = Field(min_length=1, max_length=4096)
    json_schema: str = Field(min_length=512, max_length=16384)
    website_content: str = Field(min_length=1, max_length=65536)
    llm_response: str = Field(min_length=1, max_length=32768)
    llm_model: str = Field(min_length=1, max_length=256)
    url: str = Field(min_length=1, max_length=2048)


def _build_valid_telemetry_event(
    prompt: str | None,
    schema: dict | None,
    content: str | None,
    response: dict | str | None,
    llm_model: str | None,
    source: list[str] | None,
) -> TelemetryEvent | None:
    """Build and validate a TelemetryEvent. Returns None if validation fails."""
    url: str | None = source[0] if isinstance(source, list) and source else None

    json_schema: str | None = None
    if isinstance(schema, dict):
        try:
            json_schema = json.dumps(schema)
        except (TypeError, ValueError):
            json_schema = None
    elif schema is not None:
        json_schema = str(schema)

    llm_response: str | None = None
    if isinstance(response, dict):
        try:
            llm_response = json.dumps(response)
        except (TypeError, ValueError):
            llm_response = None
    elif response is not None:
        llm_response = str(response)

    try:
        return TelemetryEvent(
            user_prompt=prompt,
            json_schema=json_schema,
            website_content=content,
            llm_response=llm_response,
            llm_model=llm_model or "unknown",
            url=url,
        )
    except (ValidationError, TypeError):
        return None


def _send_telemetry(event: TelemetryEvent):
    """Send telemetry event to the tracing endpoint."""
    headers = {
        "Content-Type": "application/json",
        "sgai-oss-version": VERSION,
    }
    try:
        data = json.dumps(event.model_dump()).encode()
    except (TypeError, ValueError) as e:
        logger.debug(f"Failed to serialize telemetry event: {e}")
        return

    try:
        req = request.Request(TRACK_URL, data=data, headers=headers)
        with request.urlopen(req, timeout=TIMEOUT) as f:
            f.read()
            if f.code == 201:
                logger.debug("Telemetry data sent successfully")
            else:
                logger.debug(f"Telemetry endpoint returned unexpected status: {f.code}")
    except HTTPError as e:
        logger.debug(f"Failed to send telemetry data (HTTP {e.code}): {e.reason}")
    except URLError as e:
        logger.debug(f"Failed to send telemetry data (URL error): {e.reason}")
    except OSError as e:
        logger.debug(f"Failed to send telemetry data (OS error): {e}")


def _send_telemetry_threaded(event: TelemetryEvent):
    """Send telemetry in a background daemon thread."""
    try:
        th = threading.Thread(target=_send_telemetry, args=(event,))
        th.daemon = True
        th.start()
    except RuntimeError as e:
        logger.debug(f"Failed to send telemetry data in a thread: {e}")


def log_event(event: str, properties: dict[str, Any]):
    """No-op stub kept for backwards compatibility."""
    logger.debug(f"log_event called with event={event} (no-op)")


def log_graph_execution(
    graph_name: str,
    source: str,
    prompt: str,
    schema: dict,
    llm_model: str,
    embedder_model: str,
    source_type: str,
    execution_time: float,
    content: str = None,
    response: dict = None,
    error_node: str = None,
    exception: str = None,
    total_tokens: int = None,
):
    """
    function for logging the graph execution
    """
    if not is_telemetry_enabled():
        return

    if error_node is not None:
        return

    event = _build_valid_telemetry_event(
        prompt=prompt,
        schema=schema,
        content=content,
        response=response,
        llm_model=llm_model,
        source=source,
    )
    if event is None:
        logger.debug("Telemetry skipped: event validation failed")
        return

    _send_telemetry_threaded(event)


def capture_function_usage(call_fn: Callable) -> Callable:
    """Passthrough decorator kept for backwards compatibility."""
    return call_fn
