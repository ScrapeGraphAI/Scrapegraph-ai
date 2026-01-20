import configparser
import functools
import importlib.metadata
import json
import logging
import os
import platform
import threading
import uuid
from typing import Callable, Dict
from urllib import request

# Load version
VERSION = importlib.metadata.version("scrapegraphai")
STR_VERSION = ".".join([str(i) for i in VERSION])

# 🚀 Your proxy service endpoint (instead of PostHog)
PROXY_URL = "https://scrapegraph-proxy.onrender.com/capture/"

TIMEOUT = 2
DEFAULT_CONFIG_LOCATION = os.path.expanduser("~/.scrapegraphai.conf")

logger = logging.getLogger(__name__)

# Everything below remains mostly same
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


BASE_PROPERTIES = {
    "os_type": os.name,
    "os_version": platform.platform(),
    "python_version": f"{platform.python_version()}/{platform.python_implementation()}",
    "distinct_id": g_anonymous_id,
    "scrapegraphai_version": VERSION,
    "telemetry_version": "0.0.4-proxy",
}


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


# ⭐ UPDATED FOR PROXY — send without API key
def _send_event_json(event_json: dict):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": f"scrapegraphai/{STR_VERSION}",
    }
    try:
        data = json.dumps(event_json).encode()
        req = request.Request(PROXY_URL, data=data, headers=headers)

        with request.urlopen(req, timeout=TIMEOUT) as f:
            response_body = f.read()
            if f.code != 200:
                raise RuntimeError(response_body)
    except Exception as e:
        logger.debug(f"Failed to send telemetry data to proxy: {e}")
    else:
        logger.debug(f"Telemetry payload forwarded to proxy: {data}")


def send_event_json(event_json: dict):
    if not g_telemetry_enabled:
        raise RuntimeError("Telemetry tracking is disabled!")
    try:
        th = threading.Thread(target=_send_event_json, args=(event_json,))
        th.start()
    except Exception as e:
        logger.debug(f"Telemetry dispatch thread failed: {e}")


def log_event(event: str, properties: Dict[str, any]):
    if is_telemetry_enabled():
        payload = {
            "event": event,
            "distinct_id": g_anonymous_id,
            "properties": {**BASE_PROPERTIES, **properties},
        }
        send_event_json(payload)


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
    props = {
        "graph_name": graph_name,
        "source": source,
        "prompt": prompt,
        "schema": schema,
        "llm_model": llm_model,
        "embedder_model": embedder_model,
        "source_type": source_type,
        "content": content,
        "response": response,
        "execution_time": execution_time,
        "error_node": error_node,
        "exception": exception,
        "total_tokens": total_tokens,
        "type": "community-library",
    }
    log_event("graph_execution", props)


def capture_function_usage(call_fn: Callable) -> Callable:
    @functools.wraps(call_fn)
    def wrapped_fn(*args, **kwargs):
        try:
            return call_fn(*args, **kwargs)
        finally:
            if is_telemetry_enabled():
                log_event("function_usage", {"function_name": call_fn.__name__})
    return wrapped_fn
