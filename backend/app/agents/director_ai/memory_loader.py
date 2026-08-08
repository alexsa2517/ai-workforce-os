"""
DirectorAI Memory Loader
Loads character, world, and episode data from knowledge base.
"""
import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("ai_workforce.agents.director_ai.memory")


class DirectorMemoryLoader:
    """Loads director AI knowledge from filesystem."""

    def __init__(self, knowledge_dir: Optional[str] = None):
        self.knowledge_dir = Path(knowledge_dir or settings.KNOWLEDGE_DIR)

    def load_character(self, name: str) -> Dict[str, Any]:
        """Load character data."""
        path = self.knowledge_dir / "characters" / f"{name}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"name": name, "description": "", "traits": []}

    def load_world(self, name: str) -> Dict[str, Any]:
        """Load world data."""
        path = self.knowledge_dir / "worlds" / f"{name}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"name": name, "description": ""}

    def load_episode(self, name: str) -> Dict[str, Any]:
        """Load episode data."""
        path = self.knowledge_dir / "episodes" / f"{name}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"name": name, "scenes": []}
