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
import functools
import importlib.metadata
import json
import os
import platform
import threading
import logging
import uuid
from typing import Callable, Dict
from urllib import request

VERSION = importlib.metadata.version("scrapegraphai")
STR_VERSION = ".".join([str(i) for i in VERSION])
HOST = "https://eu.i.posthog.com"
TRACK_URL = f"{HOST}/capture/"  # https://posthog.com/docs/api/post-only-endpoints
API_KEY = "phc_orsfU4aHhtpTSLVcUE2hdUkQDLM4OEQZndKGFBKMEtn"
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


def _check_config_and_environ_for_telemetry_flag(
    telemetry_default: bool, config_obj: configparser.ConfigParser
) -> bool:
    telemetry_enabled = telemetry_default
    if "telemetry_enabled" in config_obj["DEFAULT"]:
        try:
            telemetry_enabled = config_obj.getboolean("DEFAULT", "telemetry_enabled")
        except ValueError as e:
            logger.debug(f"Unable to parse value for `telemetry_enabled` from config. Encountered {e}")
    if os.environ.get("SCRAPEGRAPHAI_TELEMETRY_ENABLED") is not None:
        env_value = os.environ.get("SCRAPEGRAPHAI_TELEMETRY_ENABLED")
        config_obj["DEFAULT"]["telemetry_enabled"] = env_value
        try:
            telemetry_enabled = config_obj.getboolean("DEFAULT", "telemetry_enabled")
        except ValueError as e:
            logger.debug(f"Unable to parse value for `SCRAPEGRAPHAI_TELEMETRY_ENABLED` from environment. Encountered {e}")
    return telemetry_enabled


config = _load_config(DEFAULT_CONFIG_LOCATION)
g_telemetry_enabled = _check_config_and_environ_for_telemetry_flag(True, config)
g_anonymous_id = config["DEFAULT"]["anonymous_id"]
call_counter = 0
MAX_COUNT_SESSION = 1000

BASE_PROPERTIES = {
    "os_type": os.name,
    "os_version": platform.platform(),
    "python_version": f"{platform.python_version()}/{platform.python_implementation()}",
    "distinct_id": g_anonymous_id,
    "scrapegraphai_version": VERSION,
    "telemetry_version": "0.0.3",
}


def disable_telemetry():
    global g_telemetry_enabled
    g_telemetry_enabled = False


def is_telemetry_enabled() -> bool:
    if g_telemetry_enabled:
        global call_counter
        if call_counter == 0:
            logger.debug(
                "Note: ScrapeGraphAI collects anonymous usage data to improve the library. "
                "You can disable telemetry by setting SCRAPEGRAPHAI_TELEMETRY_ENABLED=false or "
                "by editing ~/.scrapegraphai.conf."
            )
        call_counter += 1
        if call_counter > MAX_COUNT_SESSION:
            return False
        return True
    else:
        return False


def _send_event_json(event_json: dict):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": f"scrapegraphai/{STR_VERSION}",
    }
    try:
        data = json.dumps(event_json).encode()
        req = request.Request(TRACK_URL, data=data, headers=headers)
        with request.urlopen(req, timeout=TIMEOUT) as f:
            res = f.read()
            if f.code != 200:
                raise RuntimeError(res)
    except Exception as e:
        logger.debug(f"Failed to send telemetry data: {e}")
    else:
        logger.debug(f"Telemetry data sent: {data}")


def send_event_json(event_json: dict):
    if not g_telemetry_enabled:
        raise RuntimeError("Telemetry tracking is disabled!")
    try:
        th = threading.Thread(target=_send_event_json, args=(event_json,))
        th.start()
    except Exception as e:
        logger.debug(f"Failed to send telemetry data in a thread: {e}")


def log_event(event: str, properties: Dict[str, any]):
    if is_telemetry_enabled():
        event_json = {
            "api_key": API_KEY,
            "event": event,
            "properties": {**BASE_PROPERTIES, **properties},
        }
        send_event_json(event_json)


def log_graph_execution(graph_name: str, source: str, prompt:str, schema:dict, llm_model: str, embedder_model: str, source_type: str, execution_time: float, content: str = None, response: dict = None, error_node: str = None, exception: str = None, total_tokens: int = None):
    properties = {
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
        "type": "community-library"
    }
    log_event("graph_execution", properties)


def capture_function_usage(call_fn: Callable) -> Callable:
    @functools.wraps(call_fn)
    def wrapped_fn(*args, **kwargs):
        try:
            return call_fn(*args, **kwargs)
        finally:
            if is_telemetry_enabled():
                try:
                    function_name = call_fn.__name__
                    log_event("function_usage", {"function_name": function_name})
                except Exception as e:
                    logger.debug(f"Failed to send telemetry for function usage. Encountered: {e}")
    return wrapped_fn