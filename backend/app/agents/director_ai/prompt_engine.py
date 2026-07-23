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
Blink Rate: {character['appearance']['eyes']['blink_rate']}
Gaze Style: {character['appearance']['eyes']['gaze_style']}
Eye Detail: {character['appearance']['eyes']['detail']}

Facial Dynamics:
Micro-expressions: {', '.join(character['appearance']['facial_dynamics']['micro_expressions'])}
Skin Texture: {character['appearance']['facial_dynamics']['skin_texture']}
Natural Movements: {character['appearance']['facial_dynamics']['natural_movements']}

Hair:
{character['appearance']['hair']['style']}

Clothing:
{character['costume']['main_outfit']}


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
