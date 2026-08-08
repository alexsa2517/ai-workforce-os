"""
Prompt Engine for DirectorAI
"""
import logging

logger = logging.getLogger("ai_workforce.agents.director_ai.prompt")


class PromptEngine:
    """Generates optimized prompts for scene creation."""

    def build_scene_prompt(self, character: dict, world: dict, scene: dict) -> str:
        """Build cinematic scene prompt."""
        return f"Cinematic scene in {world.get('name', 'unknown world')} featuring {character.get('name', 'character')}"
