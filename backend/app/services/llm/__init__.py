"""
LLM Services - Language Model provider integrations
Supports OpenAI, Google Gemini, and DeepSeek.
Robust version with resilient imports.
"""
from .factory import LLMFactory

# Attempt to export clients, but don't fail if they can't be imported
# (Factory will handle the error when requested)
try:
    from .openai import OpenAIClient
except:
    OpenAIClient = None

try:
    from .gemini import GeminiClient
except:
    GeminiClient = None

try:
    from .deepseek import DeepSeekClient
except:
    DeepSeekClient = None

__all__ = ["LLMFactory", "OpenAIClient", "GeminiClient", "DeepSeekClient"]
