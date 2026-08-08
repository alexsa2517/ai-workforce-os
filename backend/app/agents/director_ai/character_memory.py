"""
Character Memory for DirectorAI
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("ai_workforce.agents.director_ai.character")


class CharacterMemory:
    """Manages character state and memory."""

    def __init__(self):
        self._memories: Dict[str, Any] = {}

    def remember(self, character_id: str, key: str, value: Any):
        """Store character memory."""
        if character_id not in self._memories:
            self._memories[character_id] = {}
        self._memories[character_id][key] = value

    def recall(self, character_id: str, key: str) -> Any:
        """Recall character memory."""
        return self._memories.get(character_id, {}).get(key)
