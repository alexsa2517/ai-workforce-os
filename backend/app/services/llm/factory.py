from .openai import OpenAIClient
from .gemini import GeminiClient
from .deepseek import DeepSeekClient


class LLMFactory:
    """Factory สำหรับสร้าง LLM Client"""

    @staticmethod
    def get(provider: str):
        provider = provider.lower()

        providers = {
            "openai": OpenAIClient,
            "gemini": GeminiClient,
            "deepseek": DeepSeekClient,
        }

        if provider not in providers:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Available: {', '.join(providers.keys())}"
            )

        return providers[provider]()
