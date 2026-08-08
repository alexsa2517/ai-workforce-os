"""
Video Clip Planner - Uses LLM to plan video clips based on requirements.
Follows Phase 3 of the video generation workflow.
"""
import logging
import json
from typing import List, Dict, Any, Optional
from app.services.llm.factory import LLMFactory
from app.core.schemas import VideoClipPlan, VideoProjectResponse, BgmBlueprint, BgmEmotionalArcRow

logger = logging.getLogger("ai_workforce.video.clip_planner")


CLIP_PLANNER_SYSTEM_PROMPT = """You are an expert video director and screenwriter. Your task is to break down a video project into detailed clip plans.

Rules:
- Each clip should be 3-10 seconds long
- Each clip should have ONE action and ONE scene
- transition_description MUST be detailed (2-4 sentences minimum) including:
  * Subject appearance (key visual features)
  * Movement trajectory (how subject/camera moves)
  * State changes (how objects/environment change)
  * Existence statements (what is present throughout)
- Camera movements must be physically possible within the duration
- Narration text must fit within the clip duration budget
- For CJK languages (Thai, Chinese, Japanese, Korean): ~4 characters/sec
- For alphabetic languages: ~2.5 words/sec

Output JSON format with an array of clips."""


class ClipPlanner:
    """Plans video clips using LLM."""

    async def plan_clips(
        self,
        project: VideoProjectResponse,
        style_spec: Dict[str, Any],
        voice_profiles: Dict[str, Any],
        bgm_source: str,
        bgm_properties: Optional[Dict[str, Any]] = None,
        provider: str = "openai",
    ) -> List[VideoClipPlan]:
        """
        Generate clip plans for a video project.

        Args:
            project: Video project with requirements
            style_spec: Visual style specification
            voice_profiles: Voice profile definitions
            bgm_source: Background music source type
            bgm_properties: BGM properties if separate
            provider: LLM provider to use

        Returns:
            List of VideoClipPlan objects
        """
        prompt = self._build_planning_prompt(project, style_spec, voice_profiles, bgm_source, bgm_properties)

        logger.info(f"Planning clips for project {project.project_id}")

        result = await LLMFactory.generate(
            prompt=prompt,
            provider=provider,
            system_prompt=CLIP_PLANNER_SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=4000,
        )

        if result.get("error"):
            logger.error(f"Clip planning failed: {result['error']}")
            raise ValueError(f"Failed to plan clips: {result.get('detail', 'Unknown error')}")

        try:
            content = result["content"]
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            data = json.loads(content)
            clips_data = data.get("clips", data if isinstance(data, list) else [])

            clips = []
            for i, clip_data in enumerate(clips_data):
                clip = VideoClipPlan(
                    sequence_number=i,
                    narrative_purpose=clip_data.get("narrative_purpose", "establish"),
                    pacing=clip_data.get("pacing", "moderate"),
                    scene=clip_data.get("scene", ""),
                    content_action=clip_data.get("content_action", ""),
                    transition_description=clip_data.get("transition_description", ""),
                    target_duration=clip_data.get("target_duration", 5.0),
                    camera_movement=clip_data.get("camera_movement", "static"),
                    first_keyframe_framing=clip_data.get("first_keyframe_framing", ""),
                    first_keyframe_visible_content=clip_data.get("first_keyframe_visible_content", ""),
                    inter_clip_boundary=clip_data.get("inter_clip_boundary", "scene_cut"),
                    first_keyframe_reuse=clip_data.get("first_keyframe_reuse", False),
                    on_screen_dialogue=clip_data.get("on_screen_dialogue"),
                    sound_effects=clip_data.get("sound_effects"),
                    bgm_cue=clip_data.get("bgm_cue"),
                    narration_cue=clip_data.get("narration_cue"),
                    narration_budget=clip_data.get("narration_budget"),
                )
                clips.append(clip)

            logger.info(f"Planned {len(clips)} clips for project {project.project_id}")
            return clips

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse clip plan JSON: {e}")
            raise ValueError(f"Invalid clip plan format: {e}")
        except Exception as e:
            logger.error(f"Failed to process clip plan: {e}")
            raise

    def _build_planning_prompt(
        self,
        project: VideoProjectResponse,
        style_spec: Dict[str, Any],
        voice_profiles: Dict[str, Any],
        bgm_source: str,
        bgm_properties: Optional[Dict[str, Any]],
    ) -> str:
        """Build the planning prompt for LLM."""
        prompt = f"""Create a detailed clip-by-clip plan for the following video project.

## Project Requirements
- Title: {project.title}
- Description: {project.description or 'N/A'}
- Goal: {project.goal or 'N/A'}
- Target Audience: {project.target_audience or 'General'}
- Target Duration: {project.duration_target or 60} seconds
- Aspect Ratio: {project.aspect_ratio}
- Visual Style: {project.visual_style or 'N/A'}
- Language: {project.language or 'th'}

## Visual Style Specification
- Sub-genre: {style_spec.get('sub_genre', 'N/A')}
- Rendering & Line: {style_spec.get('rendering_line', 'N/A')}
- Color & Lighting: {style_spec.get('color_lighting', 'N/A')}
- Detail Density: {style_spec.get('detail_density', 'N/A')}

## Voice Profiles
{json.dumps(voice_profiles, indent=2, ensure_ascii=False)}

## BGM Configuration
- Source: {bgm_source}
"""
        if bgm_properties:
            prompt += f"""- BGM Properties:
  - Genre: {bgm_properties.get('genre_style', 'N/A')}
  - BPM: {bgm_properties.get('bpm', 'N/A')}
  - Key/Scale: {bgm_properties.get('key_scale', 'N/A')}
  - Core Instrumentation: {', '.join(bgm_properties.get('core_instrumentation', []))}
"""

        prompt += """
## Instructions
1. Break the video into clips of 3-10 seconds each
2. Each clip must have a clear narrative purpose (establish/develop/climax/resolve/transition/supplementary)
3. transition_description must be detailed (2-4 sentences) covering:
   - Subject appearance (what they look like, wear, etc.)
   - Movement trajectory (how they/camera move)
   - State changes (how things change over time)
   - Existence statements (what remains present throughout)
4. Camera movement must be physically possible in the given duration
5. If narration exists, ensure text fits within duration budget:
   - Thai/Chinese/Japanese/Korean: ~4 characters/second
   - English/Spanish/French: ~2.5 words/second
6. For continuous clips (inter_clip_boundary = "continuous"), ensure visual continuity

## Output Format
Return ONLY a JSON object with this structure:
{
  "clips": [
    {
      "sequence_number": 0,
      "narrative_purpose": "establish",
      "pacing": "moderate",
      "scene": "Description of environment",
      "content_action": "Subject + action + trajectory",
      "transition_description": "Detailed 2-4 sentence description of what happens visually...",
      "target_duration": 5.0,
      "camera_movement": "static",
      "first_keyframe_framing": "Wide shot, eye level, subject centered",
      "first_keyframe_visible_content": "Subject standing in room, window behind",
      "inter_clip_boundary": "scene_cut",
      "first_keyframe_reuse": false,
      "on_screen_dialogue": null,
      "sound_effects": null,
      "bgm_cue": {"mood": "gentle", "arrangement": "sparse"},
      "narration_cue": "Optional narration text",
      "narration_budget": 5.0
    }
  ]
}
"""
        return prompt

    async def generate_bgm_blueprint(
        self,
        clips: List[VideoClipPlan],
        bgm_properties: Dict[str, Any],
        provider: str = "openai",
    ) -> BgmBlueprint:
        """Generate BGM emotional arc blueprint from clip plans."""
        prompt = f"""Create a BGM (Background Music) Emotional Arc Blueprint based on the following clip plans.

## BGM Properties
- Genre: {bgm_properties.get('genre_style', 'N/A')}
- BPM: {bgm_properties.get('bpm', 120)}
- Key/Scale: {bgm_properties.get('key_scale', 'C major')}
- Core Instrumentation: {', '.join(bgm_properties.get('core_instrumentation', []))}

## Clip Plans
"""
        total_duration = 0
        for clip in clips:
            prompt += f"""
Clip {clip.sequence_number} ({clip.target_duration}s):
- Mood: {clip.bgm_cue.get('mood', 'N/A') if clip.bgm_cue else 'N/A'}
- Arrangement: {clip.bgm_cue.get('arrangement', 'N/A') if clip.bgm_cue else 'N/A'}
- Narrative: {clip.narrative_purpose}
"""
            total_duration += clip.target_duration

        prompt += f"""
## Instructions
1. Calculate cumulative time segments for each clip
2. Merge consecutive clips with identical mood/arrangement into single rows
3. Create a precise second-by-second emotional arc table
4. Each row must have: Time Segment, Mood/Emotion, Arrangement State (sparse/moderate/dense/full)

## Output Format
Return ONLY a JSON object:
{{
  "total_duration": {total_duration},
  "bpm": {bgm_properties.get('bpm', 120)},
  "key_scale": "{bgm_properties.get('key_scale', 'C major')}",
  "global_directives": "Instrumental only, no vocals. Create a {total_duration}s track at {bgm_properties.get('bpm', 120)} BPM.",
  "segments": [
    {{
      "time_segment": "[00:00-00:16]",
      "mood_emotion": "gentle, relaxed",
      "arrangement_state": "sparse",
      "density_brightness": "low density, warm",
      "active_instruments": ["acoustic guitar", "soft piano"]
    }}
  ]
}}
"""

        result = await LLMFactory.generate(
            prompt=prompt,
            provider=provider,
            temperature=0.5,
            max_tokens=2000,
        )

        if result.get("error"):
            raise ValueError(f"BGM blueprint generation failed: {result.get('detail')}")

        try:
            content = result["content"]
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            data = json.loads(content)

            segments = [
                BgmEmotionalArcRow(
                    time_segment=s["time_segment"],
                    mood_emotion=s["mood_emotion"],
                    arrangement_state=s["arrangement_state"],
                    density_brightness=s.get("density_brightness"),
                    active_instruments=s.get("active_instruments"),
                )
                for s in data.get("segments", [])
            ]

            return BgmBlueprint(
                total_duration=data.get("total_duration", total_duration),
                bpm=data.get("bpm", bgm_properties.get("bpm", 120)),
                key_scale=data.get("key_scale", bgm_properties.get("key_scale", "C major")),
                segments=segments,
                global_directives=data.get("global_directives", "Instrumental only, no vocals"),
            )
        except Exception as e:
            logger.error(f"Failed to parse BGM blueprint: {e}")
            raise ValueError(f"Invalid BGM blueprint format: {e}")
