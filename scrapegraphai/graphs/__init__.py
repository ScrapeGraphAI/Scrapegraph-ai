"""
This module defines the graph structures and related functionalities for the ScrapeGraphAI application.
"""

from .abstract_graph import AbstractGraph
from .base_graph import BaseGraph
from .code_generator_graph import CodeGeneratorGraph
from .csv_scraper_graph import CSVScraperGraph
from .csv_scraper_multi_graph import CSVScraperMultiGraph
from .depth_search_graph import DepthSearchGraph
from .document_scraper_graph import DocumentScraperGraph
from .document_scraper_multi_graph import DocumentScraperMultiGraph
from .json_scraper_graph import JSONScraperGraph
from .json_scraper_multi_graph import JSONScraperMultiGraph
from .omni_scraper_graph import OmniScraperGraph
from .omni_search_graph import OmniSearchGraph
from .screenshot_scraper_graph import ScreenshotScraperGraph
from .script_creator_graph import ScriptCreatorGraph
from .script_creator_multi_graph import ScriptCreatorMultiGraph
from .search_graph import SearchGraph
from .search_link_graph import SearchLinkGraph
from .smart_scraper_graph import SmartScraperGraph
from .smart_scraper_lite_graph import SmartScraperLiteGraph
from .smart_scraper_multi_concat_graph import SmartScraperMultiConcatGraph
from .smart_scraper_multi_graph import SmartScraperMultiGraph
from .smart_scraper_multi_lite_graph import SmartScraperMultiLiteGraph
from .speech_graph import SpeechGraph
from .xml_scraper_graph import XMLScraperGraph
from .xml_scraper_multi_graph import XMLScraperMultiGraph

__all__ = [
    # Base graphs
    "AbstractGraph",
    "BaseGraph",
    # Specialized scraper graphs
    "CSVScraperGraph",
    "CSVScraperMultiGraph",
    "DocumentScraperGraph",
    "DocumentScraperMultiGraph",
    "JSONScraperGraph",
    "JSONScraperMultiGraph",
    "XMLScraperGraph",
    "XMLScraperMultiGraph",
    # Smart scraper variants
    "SmartScraperGraph",
    "SmartScraperLiteGraph",
    "SmartScraperMultiGraph",
    "SmartScraperMultiLiteGraph",
    "SmartScraperMultiConcatGraph",
    # Search-related graphs
    "SearchGraph",
    "SearchLinkGraph",
    "DepthSearchGraph",
    "OmniSearchGraph",
    # Other specialized graphs
    "CodeGeneratorGraph",
    "OmniScraperGraph",
    "ScreenshotScraperGraph",
    "ScriptCreatorGraph",
    "ScriptCreatorMultiGraph",
    "SpeechGraph",
]
