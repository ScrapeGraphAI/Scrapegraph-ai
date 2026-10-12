"""
This module contains the model definitions used in the ScrapeGraphAI application.
"""

from .atlascloud import AtlasCloud
from .cheaperinference import CheaperInference
from .clod import CLoD
from .deepseek import DeepSeek
from .litellm import LiteLLM
from .minimax import MiniMax
from .nvidia import Nvidia
from .oneapi import OneApi
from .openai_itt import OpenAIImageToText
from .openai_tts import OpenAITextToSpeech
from .xai import XAI

__all__ = ["AtlasCloud", "CheaperInference", "DeepSeek", "LiteLLM", "MiniMax", "OneApi", "OpenAIImageToText", "OpenAITextToSpeech", "CLoD", "XAI", "Nvidia"]
