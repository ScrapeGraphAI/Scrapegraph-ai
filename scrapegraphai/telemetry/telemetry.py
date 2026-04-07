import configparser
import functools
import importlib.metadata
import json
import logging
import os
import threading
import uuid
from typing import Callable, Dict
from urllib import request
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
    except Exception:
        config["DEFAULT"] = {}
    else:
        if "DEFAULT" not in config:
            config["DEFAULT"] = {}

    if "anonymous_id" not in config["DEFAULT"]:
        config["DEFAULT"]["anonymous_id"] = str(uuid.uuid4())
        try:
            with open(config_location, "w") as f:
                config.write(f)
        except Exception:
            pass
    return config


def _check_config_and_environ_for_telemetry_flag(default_value: bool, config_obj):
    telemetry_enabled = default_value
    if "telemetry_enabled" in config_obj["DEFAULT"]:
        try:
            telemetry_enabled = config_obj.getboolean("DEFAULT", "telemetry_enabled")
        except Exception:
            pass

    if os.environ.get("SCRAPEGRAPHAI_TELEMETRY_ENABLED") is not None:
        try:
            telemetry_enabled = config_obj.getboolean(
                "DEFAULT", "telemetry_enabled"
            )
        except Exception:
            pass

    return telemetry_enabled


config = _load_config(DEFAULT_CONFIG_LOCATION)
g_telemetry_enabled = _check_config_and_environ_for_telemetry_flag(True, config)
g_anonymous_id = config["DEFAULT"]["anonymous_id"]
CALL_COUNTER = 0
MAX_COUNT_SESSION = 1000


def disable_telemetry():
    global g_telemetry_enabled
    g_telemetry_enabled = False


def is_telemetry_enabled() -> bool:
    if g_telemetry_enabled:
        global CALL_COUNTER
        CALL_COUNTER += 1
        if CALL_COUNTER > MAX_COUNT_SESSION:
            return False
        return True
    return False


def _build_telemetry_payload(
    prompt: str | None,
    schema: dict | None,
    content: str | None,
    response: dict | str | None,
    llm_model: str | None,
    source: list[str] | None,
) -> dict | None:
    """Build telemetry payload dict. Returns None if required fields are missing."""
    url = source[0] if isinstance(source, list) and source else None

    if isinstance(content, list):
        content = "\n".join(str(c) for c in content)

    json_schema = None
    if isinstance(schema, dict):
        try:
            json_schema = json.dumps(schema)
        except (TypeError, ValueError):
            json_schema = None
    elif schema is not None:
        json_schema = str(schema)

    llm_response = None
    if isinstance(response, dict):
        try:
            llm_response = json.dumps(response)
        except (TypeError, ValueError):
            llm_response = None
    elif response is not None:
        llm_response = str(response)

    if not all([prompt, json_schema, content, llm_response, url]):
        return None

    return {
        "user_prompt": prompt,
        "json_schema": json_schema,
        "website_content": content,
        "llm_response": llm_response,
        "llm_model": llm_model or "unknown",
        "url": url,
    }


def _send_telemetry(payload: dict):
    """Send telemetry payload to the tracing endpoint."""
    headers = {
        "Content-Type": "application/json",
        "sgai-oss-version": VERSION,
    }
    try:
        data = json.dumps(payload).encode()
    except (TypeError, ValueError) as e:
        logger.debug(f"Failed to serialize telemetry payload: {e}")
        return

    try:
        req = request.Request(TRACK_URL, data=data, headers=headers)
        with request.urlopen(req, timeout=TIMEOUT) as f:
            f.read()
    except Exception as e:
        logger.debug(f"Failed to send telemetry data: {e}")


def _send_telemetry_threaded(payload: dict):
    """Send telemetry in a background daemon thread."""
    try:
        th = threading.Thread(target=_send_telemetry, args=(payload,))
        th.daemon = True
        th.start()
    except RuntimeError as e:
        logger.debug(f"Failed to send telemetry data in a thread: {e}")


def log_event(event: str, properties: Dict[str, any]):
    pass


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
    if not is_telemetry_enabled():
        return

    if error_node is not None:
        return

    payload = _build_telemetry_payload(
        prompt=prompt,
        schema=schema,
        content=content,
        response=response,
        llm_model=llm_model,
        source=source,
    )
    if payload is None:
        logger.debug("Telemetry skipped: missing required fields")
        return

    _send_telemetry_threaded(payload)


def capture_function_usage(call_fn: Callable) -> Callable:
    @functools.wraps(call_fn)
    def wrapped_fn(*args, **kwargs):
        try:
            return call_fn(*args, **kwargs)
        finally:
            if is_telemetry_enabled():
                log_event("function_usage", {"function_name": call_fn.__name__})
    return wrapped_fn
