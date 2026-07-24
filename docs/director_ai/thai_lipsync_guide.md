# Thai Lip-sync & Emotional Articulation Guide

This document explains how the advanced Thai Lip-sync system works in Director AI.

## Overview
The system is designed to handle the complexity of Thai phonetics, including:
- **Tonal Inflections:** Mouth and facial tension changes based on the 5 Thai tones.
- **Vowel Duration:** Precise mouth shapes for short vs. long vowels.
- **Emotional Weight:** Syncing lip movements with the character's emotional state.

## Configuration in `linhfeng.json`
The `speech_dynamics` section defines how the character speaks:

```json
"speech_dynamics": {
  "lip_sync_precision": "ultra-high",
  "thai_articulation": {
    "vowels": "precise mouth opening for Thai long/short vowels",
    "consonants": "accurate labial/dental placement",
    "tone_influence": "facial muscle tension changes based on tones"
  },
  "emotional_sync": {
    "anger": "wide movements",
    "sadness": "quivering lips",
    "joy": "upward corners",
    "determined": "firm movements"
  }
}
```

## How to Use
When generating a scene, the `PromptEngine` automatically extracts these rules and combines them with the scene's emotion to create a highly detailed instruction for video generation models (like Runway, Kling, or Luma).

### Example Prompt Output
The engine will generate instructions like:
> "Ensure every Thai syllable is perfectly synced with realistic mouth shapes, emphasizing the emotional weight of the Thai dialogue. Mouth corners should quiver slightly to reflect the 'Sadness' emotion as per character rules."
