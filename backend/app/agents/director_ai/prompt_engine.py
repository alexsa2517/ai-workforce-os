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


Style:
Realistic fantasy film,
4K,
cinematic quality.
"""

        return prompt
