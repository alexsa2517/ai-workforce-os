"""
Prompt Engine - Generates structured prompts for cinematic AI generation
Creates scene prompts, character descriptions, world descriptions,
and emotion-based prompts for image and video generation.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("ai_workforce.agents.prompt_engine")


class PromptEngine:
    """Engine for generating structured cinematic prompts."""

    def __init__(self):
        self.default_style = "cinematic, photorealistic, 4K quality"

    def create_scene_prompt(
        self,
        character: Dict[str, Any],
        world: Dict[str, Any],
        scene: Dict[str, Any],
    ) -> str:
        """
        Create a detailed scene prompt for image/video generation.

        Args:
            character: Character data from knowledge base
            world: World data from knowledge base
            scene: Scene data from episode

        Returns:
            Detailed scene prompt string
        """
        char_name = character.get("name", "Unknown")
        char_english = character.get("english_name", char_name)
        appearance = character.get("appearance", {})
        face = appearance.get("face", {}).get("description", "")
        hair = appearance.get("hair", {})
        hair_desc = f"{hair.get('color', 'black')} {hair.get('style', 'hair')}"
        costume = character.get("costume", {}).get("main_outfit", "traditional outfit")

        world_name = world.get("name", "Unknown world")
        locations = world.get("locations", [])
        location = scene.get("location", locations[0]["name"] if locations else "unknown")

        scene_title = scene.get("title", "")
        action = scene.get("action", "")
        emotion = scene.get("emotion", "neutral")
        time_of_day = scene.get("time", "")

        prompt = (
            f"Cinematic scene: {char_name} ({char_english}) in {world_name}. "
            f"Location: {location}. "
            f"Character appearance: {face}, hair: {hair_desc}, wearing {costume}. "
            f"Action: {action}. "
            f"Emotion: {emotion}. "
            f"Time: {time_of_day}. "
            f"Style: {self.default_style}. "
            f"Lighting: natural, dramatic shadows. "
            f"Camera: medium shot, slight angle."
        )
        return prompt

    def create_character_prompt(self, character: Dict[str, Any], emotion: str = "neutral") -> str:
        """
        Create a character portrait prompt.

        Args:
            character: Character data
            emotion: Target emotion for the portrait

        Returns:
            Character portrait prompt
        """
        char_name = character.get("name", "Unknown")
        char_english = character.get("english_name", char_name)
        appearance = character.get("appearance", {})
        face = appearance.get("face", {}).get("description", "")
        hair = appearance.get("hair", {})
        hair_desc = f"{hair.get('color', 'black')} {hair.get('style', 'hair')}"
        costume = character.get("costume", {}).get("main_outfit", "traditional outfit")
        gender = character.get("basic_information", {}).get("gender", "male")

        prompt = (
            f"Cinematic portrait of a {gender}, "
            f"name: {char_name} ({char_english}). "
            f"Face: {face}. Hair: {hair_desc}. "
            f"Wearing: {costume}. "
            f"Emotion: {emotion}. "
            f"Style: {self.default_style}. "
            f"Lighting: soft, cinematic, Rembrandt lighting. "
            f"Background: subtle gradient, out of focus."
        )
        return prompt

    def create_world_prompt(self, world: Dict[str, Any]) -> str:
        """
        Create a world/environment prompt.

        Args:
            world: World data

        Returns:
            World environment prompt
        """
        name = world.get("name", "Unknown world")
        era = world.get("era", "Unknown era")
        description = world.get("description", "")
        locations = world.get("locations", [])
        location_desc = ", ".join(
            [loc.get("name", "") for loc in locations]
        ) if locations else ""

        prompt = (
            f"World environment: {name}. "
            f"Era: {era}. "
            f"Description: {description}. "
            f"Key locations: {location_desc}. "
            f"Style: {self.default_style}. "
            f"Atmosphere: immersive, detailed, atmospheric lighting."
        )
        return prompt

    def create_emotion_prompt(self, emotion: str, intensity: str = "moderate") -> str:
        """
        Create an emotion-specific prompt modifier.

        Args:
            emotion: Target emotion
            intensity: Intensity level (subtle, moderate, intense)

        Returns:
            Emotion prompt modifier string
        """
        emotion_map = {
            "happy": "warm smile, bright eyes, relaxed posture",
            "sad": "downcast eyes, slight frown, subdued expression",
            "angry": "furrowed brows, clenched jaw, intense gaze",
            "fearful": "wide eyes, tense expression, slight recoil",
            "surprised": "raised eyebrows, slightly open mouth",
            "neutral": "calm expression, steady gaze, composed",
            "confused": "slightly furrowed brows, tilted head, uncertain expression",
            "determined": "firm jaw, focused eyes, strong posture",
        }
        facial_expr = emotion_map.get(emotion, "neutral expression")

        intensity_map = {
            "subtle": "subtle",
            "moderate": "moderate",
            "intense": "intense",
        }
        level = intensity_map.get(intensity, "moderate")

        return f"Facial expression: {level} {facial_expr}, {level} body language matching {emotion} emotion"

    def create_dialogue_prompt(self, character: Dict[str, Any], dialogue: str) -> str:
        """
        Create a prompt for lip-sync generation with dialogue.

        Args:
            character: Character data
            dialogue: The dialogue text

        Returns:
            Dialogue prompt with character context
        """
        char_name = character.get("name", "Unknown")
        voice_data = character.get("voice", {})
        voice_desc = voice_data.get("description", "natural speaking voice")

        prompt = (
            f"Character: {char_name}. "
            f"Voice: {voice_desc}. "
            f"Dialogue: \'{dialogue}\' "
            f"Speak naturally with appropriate emotional inflection."
        )
        return prompt
