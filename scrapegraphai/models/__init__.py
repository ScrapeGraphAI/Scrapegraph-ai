"""
This module contains the model definitions used in the ScrapeGraphAI application.
"""

from .clod import CLoD
from .deepseek import DeepSeek
from .nvidia import Nvidia
from .oneapi import OneApi
from .openai_itt import OpenAIImageToText
from .openai_tts import OpenAITextToSpeech
from .xai import XAI

__all__ = ["DeepSeek", "OneApi", "OpenAIImageToText", "OpenAITextToSpeech", "CLoD", "XAI", "Nvidia"]
