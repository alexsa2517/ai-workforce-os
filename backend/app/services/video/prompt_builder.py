"""
Video Prompt Builder - Constructs optimized prompts for video generation.
Follows Phase 5 execution rules.
"""
import logging
from typing import Dict, Any, Optional
from app.core.schemas import VideoClipPlan

logger = logging.getLogger("ai_workforce.video.prompt_builder")


class VideoPromptBuilder:
    """Builds video generation prompts following best practices."""

    def build_keyframe_prompt(
        self,
        clip: VideoClipPlan,
        style_spec: Dict[str, Any],
        reference_images: Optional[list] = None,
    ) -> str:
        """
        Build first keyframe generation prompt.

        Args:
            clip: Clip plan
            style_spec: Visual style specification
            reference_images: List of reference image URLs/paths

        Returns:
            Optimized image generation prompt
        """
        prompt_parts = [
            f"Style: {style_spec.get('sub_genre', '')}, {style_spec.get('rendering_line', '')}",
            f"Scene: {clip.scene}",
            f"Framing: {clip.first_keyframe_framing}",
            f"Visible content: {clip.first_keyframe_visible_content}",
        ]

        if clip.on_screen_dialogue:
            char_name = list(clip.on_screen_dialogue.keys())[0]
            dialogue = clip.on_screen_dialogue[char_name]
            prompt_parts.append(f"Character: {char_name} speaking, expression matching dialogue")

        prompt_parts.append("High quality, detailed, cinematic lighting")
        prompt_parts.append("no text, no watermarks, no logos, no labels, no annotations")

        return ". ".join(prompt_parts)

    def build_video_prompt(
        self,
        clip: VideoClipPlan,
        style_spec: Dict[str, Any],
        has_keyframe: bool = True,
    ) -> str:
        """
        Build video generation prompt.

        Args:
            clip: Clip plan
            style_spec: Visual style specification
            has_keyframe: Whether a first keyframe is provided

        Returns:
            Detailed video generation prompt
        """
        prompt_parts = [
            f"Visual style: {style_spec.get('sub_genre', '')}, {style_spec.get('color_lighting', '')}",
            f"Pacing: {clip.pacing}",
        ]

        # Transition description (CRITICAL - must be detailed)
        prompt_parts.append(f"Action: {clip.transition_description}")

        # Subject appearance for consistency
        prompt_parts.append(f"Subject: {clip.content_action}")

        # Scene
        prompt_parts.append(f"Environment: {clip.scene}")

        # Camera movement
        if clip.camera_movement != "static":
            prompt_parts.append(f"Camera: {clip.camera_movement} movement, smooth and cinematic")

        # Audio instructions
        if clip.on_screen_dialogue:
            char_name = list(clip.on_screen_dialogue.keys())[0]
            dialogue = clip.on_screen_dialogue[char_name]
            prompt_parts.append(
                f'On-screen dialogue: {char_name} says "{dialogue}" with natural lip sync'
            )

        if clip.sound_effects:
            prompt_parts.append(f"Sound effects: {', '.join(clip.sound_effects)}")

        # BGM handling
        if clip.bgm_cue and clip.bgm_cue.get("source") == "embedded":
            prompt_parts.append(
                f"Background music: {clip.bgm_cue.get('style', '')} at {clip.bgm_cue.get('bpm', '')} BPM, "
                f"instruments: {', '.join(clip.bgm_cue.get('instruments', []))}"
            )
        else:
            prompt_parts.append("No background music.")

        # Quality modifiers
        prompt_parts.append("High quality, cinematic, smooth motion, consistent lighting")

        return ". ".join(prompt_parts)

    def build_reference_image_prompt(
        self,
        element_name: str,
        element_description: str,
        style_spec: Dict[str, Any],
        shot_type: str = "full_body",
    ) -> str:
        """
        Build reference image prompt for Phase 4.

        Args:
            element_name: Character/object name
            element_description: Appearance description
            style_spec: Visual style
            shot_type: Type of shot (full_body, face_closeup, etc.)

        Returns:
            Reference image prompt
        """
        prompt_parts = [
            f"Style: {style_spec.get('sub_genre', '')}, {style_spec.get('rendering_line', '')}, {style_spec.get('color_lighting', '')}",
            f"Subject: {element_name}, {element_description}",
            f"Shot: {shot_type}, white background, isolated subject",
            "Character design sheet, consistent appearance",
            "no text, no watermarks, no logos, no labels, no annotations",
        ]

        return ". ".join(prompt_parts)

    def build_bgm_prompt(self, blueprint: Dict[str, Any]) -> str:
        """Build music generation prompt from BGM blueprint."""
        segments = blueprint.get("segments", [])

        prompt_parts = [
            blueprint.get("global_directives", "Instrumental only, no vocals"),
            f"Create a {blueprint.get('total_duration', 60)}s track at {blueprint.get('bpm', 120)} BPM in {blueprint.get('key_scale', 'C major')}.",
            f"Genre: {blueprint.get('genre_style', 'cinematic')}",
            f"Core instrumentation: {', '.join(blueprint.get('core_instrumentation', ['piano', 'strings']))}",
        ]

        # Add arrangement breakdown
        for seg in segments:
            prompt_parts.append(
                f"[{seg.get('time_segment', '')}] {seg.get('mood_emotion', '')} - "
                f"{seg.get('arrangement_state', 'moderate')} arrangement"
            )
            if seg.get("active_instruments"):
                prompt_parts.append(f"  Instruments: {', '.join(seg['active_instruments'])}")

        return "\n".join(prompt_parts)

    def build_narration_ssml(
        self,
        text: str,
        voice_profile: Dict[str, Any],
        language: str = "th",
    ) -> str:
        """
        Build SSML for TTS narration.

        Args:
            text: Narration text
            voice_profile: Voice profile config
            language: Language code

        Returns:
            SSML string
        """
        # Basic SSML wrapping - can be extended with prosody, breaks, etc.
        ssml = f"""<speak>
<text>{text}</text>
</speak>"""
        return ssml
