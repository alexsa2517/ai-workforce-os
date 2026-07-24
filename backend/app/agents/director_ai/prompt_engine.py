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
Thai Phonetic Articulation:
- Vowels: {character['appearance']['facial_dynamics']['speech_dynamics']['thai_articulation']['vowels']}
- Consonants: {character['appearance']['facial_dynamics']['speech_dynamics']['thai_articulation']['consonants']}
- Tonal Influence: {character['appearance']['facial_dynamics']['speech_dynamics']['thai_articulation']['tone_influence']}
Jaw & Tongue: {character['appearance']['facial_dynamics']['speech_dynamics']['jaw_movement']}, {character['appearance']['facial_dynamics']['speech_dynamics']['tongue_visibility']}
Emotional Integration: The mouth movements must adapt to the emotion "{scene['emotion']}" as defined in the character's emotional sync rules (e.g., {character['appearance']['facial_dynamics']['speech_dynamics']['emotional_sync'].get(scene['emotion'].lower(), 'natural adaptation')}).
Facial Muscle Sync: {character['appearance']['facial_dynamics']['speech_dynamics']['secondary_motion']}
Instructions: Ensure every Thai syllable is perfectly synced with realistic mouth shapes, emphasizing the emotional weight of the Thai dialogue.

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

    Environmental Interaction:
Lighting Response: {character['appearance']['body']['environmental_interaction']['lighting_response']}
Weather Response: {character['appearance']['body']['environmental_interaction']['weather_response']}
Physics & Terrain: {character['appearance']['body']['environmental_interaction']['physics_interaction']}
Spatial Awareness: {character['appearance']['body']['environmental_interaction']['spatial_awareness']}
Integration: Ensure the character feels grounded in the world, reacting to the lighting, atmosphere, and physical elements of the scene.


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
