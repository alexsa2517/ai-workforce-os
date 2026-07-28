"""
Character Memory - Persistent character state management
Manages character dialogue history, emotional states, and conversation context.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ai_workforce.agents.character_memory")


class CharacterMemory:
    """Persistent memory for character state and conversation history."""

    def __init__(self, storage_path: Optional[str] = None):
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.conversations: Dict[str, List[Dict[str, Any]]] = {}
        self.storage_path = storage_path

    def add_character(self, name: str, data: Dict[str, Any]) -> None:
        """Add or update a character."""
        self.characters[name] = {
            **data,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if name not in self.conversations:
            self.conversations[name] = []
        logger.info(f"Character added/updated: {name}")

    def get_character(self, name: str) -> Optional[Dict[str, Any]]:
        """Get character data."""
        return self.characters.get(name)

    def list_characters(self) -> List[str]:
        """List all character names."""
        return list(self.characters.keys())

    def remove_character(self, name: str) -> bool:
        """Remove a character."""
        if name in self.characters:
            del self.characters[name]
            self.conversations.pop(name, None)
            logger.info(f"Character removed: {name}")
            return True
        return False

    def add_conversation(self, character_name: str, message: str, role: str = "user") -> None:
        """Add a conversation entry for a character."""
        if character_name not in self.conversations:
            self.conversations[character_name] = []
        self.conversations[character_name].append({
            "role": role,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_conversations(self, character_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent conversation history for a character."""
        convos = self.conversations.get(character_name, [])
        return convos[-limit:]

    def get_context(self, character_name: str) -> str:
        """Get a summary context string for the character."""
        char = self.get_character(character_name)
        if not char:
            return ""

        name = char.get("name", character_name)
        role = char.get("role", "Unknown")
        backstory = char.get("story", {}).get("backstory", "")

        context = f"Character: {name}\nRole: {role}\n"
        if backstory:
            context += f"Backstory: {backstory}\n"

        # Add recent conversation context
        recent = self.get_conversations(character_name, limit=5)
        if recent:
            context += "Recent context:\n"
            for msg in recent:
                context += f"  [{msg['role']}]: {msg['message'][:100]}\n"

        return context

    def clear_conversations(self, character_name: Optional[str] = None) -> None:
        """Clear conversation history."""
        if character_name:
            self.conversations.pop(character_name, None)
        else:
            self.conversations.clear()

    def save(self, path: Optional[str] = None) -> None:
        """Save character data to file."""
        save_path = Path(path or self.storage_path or "character_memory.json")
        save_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "characters": self.characters,
            "conversations": self.conversations,
        }
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Character memory saved to {save_path}")

    def load(self, path: Optional[str] = None) -> None:
        """Load character data from file."""
        load_path = Path(path or self.storage_path or "character_memory.json")
        if not load_path.exists():
            logger.warning(f"Character memory file not found: {load_path}")
            return
        with open(load_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.characters = data.get("characters", {})
        self.conversations = data.get("conversations", {})
        logger.info(f"Character memory loaded from {load_path}")
