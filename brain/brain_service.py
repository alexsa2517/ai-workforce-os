"""
Brain Service - Core reasoning and decision-making engine
Coordinates between LLM providers and application logic.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ai_workforce.brain")


class BrainService:
    """Central reasoning engine for AI Workforce OS."""

    def __init__(self):
        self.providers = {}

    def register_provider(self, name: str, provider: Any):
        """Register an LLM provider."""
        self.providers[name] = provider
        logger.info(f"Registered provider: {name}")

    async def reason(
        self,
        query: str,
        provider: str = "openai",
        context: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate a reasoned response using the specified provider.

        Args:
            query: User query
            provider: LLM provider name
            context: Optional context for the reasoning
            temperature: Sampling temperature

        Returns:
            Dict with response and metadata
        """
        llm = self.providers.get(provider)
        if not llm:
            return {"error": f"Provider '{provider}' not found", "response": ""}

        system_prompt = "You are an AI assistant for AI Workforce OS. Provide helpful, accurate responses."
        if context:
            system_prompt += f"\nContext:\n{context}"

        try:
            result = llm.generate(
                prompt=query,
                temperature=temperature,
                system_prompt=system_prompt,
            )
            return {
                "response": result.get("content", ""),
                "usage": result.get("usage", {}),
                "provider": provider,
            }
        except Exception as e:
            logger.error(f"Brain reasoning error: {e}", exc_info=True)
            return {"error": str(e), "response": ""}

    def get_available_providers(self) -> list:
        """List available providers."""
        return list(self.providers.keys())


# Singleton instance
brain = BrainService()
