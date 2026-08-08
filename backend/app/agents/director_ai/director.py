"""
DirectorAI - AI Director agent
"""
import logging
from typing import Any, Dict
from .memory_loader import DirectorMemoryLoader

logger = logging.getLogger("ai_workforce.agents.director_ai")


class DirectorAI:
    """AI Director for cinematic scene generation."""

    def __init__(self):
        self.memory = DirectorMemoryLoader()

    async def create_scene(
        self,
        character: str = "linhfeng",
        world: str = "ancient-world",
        episode: str = "ep001",
        scene_index: int = 0,
    ) -> Dict[str, Any]:
        """Create a cinematic scene."""
        char_data = self.memory.load_character(character)
        world_data = self.memory.load_world(world)
        episode_data = self.memory.load_episode(episode)

        scenes = episode_data.get("scenes", [])
        scene = scenes[scene_index] if scene_index < len(scenes) else {}

        return {
            "episode": episode,
            "scene_index": scene_index,
            "scene_prompt": scene.get("prompt", ""),
            "dialogue": scene.get("dialogue", ""),
            "characters": [character],
            "metadata": {
                "world": world_data,
                "character": char_data,
            }
        }
