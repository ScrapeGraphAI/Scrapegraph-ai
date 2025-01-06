"""
This module contains the telemetry module for the scrapegraphai package.
"""

from .telemetry import disable_telemetry, log_event, log_graph_execution

__all__ = [
    "disable_telemetry",
    "log_event",
    "log_graph_execution",
]
