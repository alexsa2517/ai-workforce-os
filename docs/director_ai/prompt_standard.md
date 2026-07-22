# Director AI Prompt Standard v1.0

## 1. Purpose

This document defines the standard prompt structure
used by Director AI for AI image and video generation.

Goals:
- Maintain character consistency
- Maintain visual style consistency
- Generate cinematic quality scenes
- Support long-running episodic storytelling


# 2. Prompt Structure

Every scene prompt MUST contain:

1. Scene Identity
2. Character Identity
3. Environment
4. Action
5. Camera Direction
6. Lighting
7. Emotion
8. Dialogue
9. Audio
10. Style


# 3. Scene Identity

Format:

EP:
Scene:
Title:
Time:
Location:


Example:

EP1
Scene 1
Title: The Mist Forest
Time: Dawn
Location: Ancient mysterious forest


# 4. Character Identity Standard

Every character prompt MUST include:

- Name
- Age range
- Gender
- Face description
- Hair style
- Clothing
- Body type
- Personality
- Unique features


Example:

Character:
Lin Feng

Age:
25

Appearance:
Young Asian male,
sharp facial features,
long black hair,
dark traditional warrior clothing.


Consistency Rule:

The same character MUST keep:
- Same face
- Same hairstyle
- Same costume
- Same visual identity


# 5. Environment Standard

Every scene must define:

- Location
- Era
- Weather
- Atmosphere
- Background elements


Example:

Ancient fantasy forest,
heavy morning fog,
giant trees,
mysterious atmosphere,
soft sunlight through leaves.


# 6. Action Description

Describe:

- Character movement
- Body language
- Facial expression
- Interaction


Example:

The character slowly walks forward,
looking around carefully,
holding an ancient sword.


# 7. Camera Direction

Every video prompt should include:

Camera:
- Shot type
- Movement
- Lens feeling


Examples:

Close-up:
Emotional facial expression

Wide shot:
Show environment

Tracking shot:
Follow character movement

Slow motion:
Emotional moment


# 8. Lighting Standard

Define:

- Time
- Light source
- Mood


Examples:

Cinematic moonlight

Golden sunrise light

Dark mysterious atmosphere


# 9. Dialogue Standard

All character dialogue:

Language:
Thai

Voice:
Natural Thai pronunciation

Emotion:
Defined by scene


Format:

Character:
Dialogue:


Example:

Lin Feng:

"ข้าต้องค้นหาความจริงของอดีต..."


# 10. Audio Standard

Include:

- Background music
- Environment sound
- Character voice


Example:

Audio:
Mystical fantasy music,
forest wind,
Thai voice narration.


# 11. Video Style Standard

Default style:

Cinematic fantasy movie,
realistic details,
high quality,
4K,
dramatic lighting,
movie camera.


# 12. Negative Prompt Rules

Avoid:

- Changing character face
- Different hairstyle
- Different costume
- Extra characters
- Wrong era
- Cartoon style (unless requested)
- Unnatural movement


# 13. Director AI Master Prompt Template


Create a cinematic scene:

[SCENE]

Character:
[CHARACTER DETAILS]

Environment:
[LOCATION DETAILS]

Action:
[ACTION]

Camera:
[CAMERA]

Lighting:
[LIGHT]

Dialogue:
[THAI DIALOGUE]

Audio:
[SOUND]

Style:
[CINEMATIC STYLE]


# 14. Quality Check Before Generation

Director AI MUST verify:

☑ Character matches Character Bible

☑ Scene matches Story Timeline

☑ Dialogue matches emotion

☑ Camera is cinematic

☑ Prompt contains enough visual details

☑ Thai voice instruction included


# 15. Version Control

Current Version:
Director AI Prompt Standard v1.0

Owner:
AI Workforce OS

Status:
Draft / Under Development
