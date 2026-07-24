class PromptEngine:

    def create_scene_prompt(
        self,
        character,
        world,
        scene
    ):

        prompt = f"""
Cinematic fantasy movie scene.

Character:
{character['name']}

Appearance:
{character['appearance']['face']['description']}

    Eyes:
Color: {character['appearance']['eyes']['color']}
Expression: {character['appearance']['eyes']['expression']}
Blink Behavior: {character['appearance']['eyes']['blink_rate']}
Gaze Dynamics: {character['appearance']['eyes']['gaze_style']}
Eye Contact: {character['appearance']['eyes']['eye_contact']}
Micro-Movements: {character['appearance']['eyes']['micro_movements']}
Detail: {character['appearance']['eyes']['detail']}

    Facial Dynamics:
Micro-expressions: {', '.join(character['appearance']['facial_dynamics']['micro_expressions'])}
Blinking Style: {character['appearance']['facial_dynamics']['blinking_behavior']}
Skin & Texture: {character['appearance']['facial_dynamics']['skin_texture']}
Natural Idle Movements: {character['appearance']['facial_dynamics']['natural_movements']}

    Speech & Lip-Sync:
Lip-Sync Precision: {character['appearance']['facial_dynamics']['speech_dynamics']['lip_sync_precision']}
Jaw Movement: {character['appearance']['facial_dynamics']['speech_dynamics']['jaw_movement']}
Tongue Visibility: {character['appearance']['facial_dynamics']['speech_dynamics']['tongue_visibility']}
Facial Muscle Sync: {character['appearance']['facial_dynamics']['speech_dynamics']['secondary_motion']}
Thai Articulation: Ensure mouth shapes (visemes) perfectly match Thai phonemes and emotional intensity of the dialogue.

Hair:
{character['appearance']['hair']['style']}

Clothing:
{character['costume']['main_outfit']}

    Body & Posture:
Posture: {character['appearance']['body']['posture']['base_stance']}
Idle Behavior: {character['appearance']['body']['posture']['idle_behavior']}
Shoulder Movement: {character['appearance']['body']['posture']['shoulder_dynamics']}

    Hand & Arm Gestures:
Gesture Style: {character['appearance']['body']['hand_gestures']['style']}
Finger Detail: {character['appearance']['body']['hand_gestures']['finger_detail']}
Speech-Driven Gestures: {character['appearance']['body']['hand_gestures']['speech_gestures']}
Movement Transitions: {character['appearance']['body']['hand_gestures']['interaction']}


World:
{world['description']}


Scene:
{scene['title']}

Action:
{scene['action']}


Emotion:
{scene['emotion']}


Camera:
Cinematic camera movement,
movie style,
dramatic lighting.


Dialogue:
Thai language,
natural Thai voice.

Audio/Speech Instructions:
Voice Profile: {character['voice']['archetype']} ({character['voice']['gender']})
Estimated Age: {character['voice']['age_years']} years old
Tone: {character['voice']['tone']}
Pitch: {character['voice']['pitch']}
Speed: {character['voice']['speed']}
Vocal Traits: {', '.join(character['voice']['vocal_traits'])}
Speech Style: Natural Thai articulation with emotional depth corresponding to {scene['emotion']}


Style:
Realistic fantasy film,
4K,
cinematic quality.
"""

        return prompt
