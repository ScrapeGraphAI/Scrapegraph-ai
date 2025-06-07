"""
__init__.py file for scrapegraphai folder
"""

from .utils.logging import get_logger, set_verbosity_info

logger = get_logger(__name__)
set_verbosity_info()
logger.info("This is an open-source library. If you want proxy rotations, residential proxies and faster inference times visit https://scrapegraphai.com")
