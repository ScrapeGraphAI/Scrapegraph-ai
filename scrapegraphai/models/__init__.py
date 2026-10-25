"""
This module contains the model definitions used in the ScrapeGraphAI application.
"""

from .atlascloud import AtlasCloud
from .cheaperinference import CheaperInference
from .clod import CLoD
from .deepseek import DeepSeek
from .minimax import MiniMax
from .nvidia import Nvidia
from .oneapi import OneApi
from .openai_itt import OpenAIImageToText
from .openai_tts import OpenAITextToSpeech
from .runcrate import Runcrate
from .xai import XAI

__all__ = ["AtlasCloud", "CheaperInference", "DeepSeek", "MiniMax", "OneApi", "OpenAIImageToText", "OpenAITextToSpeech", "Runcrate", "CLoD", "XAI", "Nvidia"]
