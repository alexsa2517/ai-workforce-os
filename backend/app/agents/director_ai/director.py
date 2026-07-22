from .memory_loader import DirectorMemoryLoader
from .prompt_engine import PromptEngine


class DirectorAI:

    def __init__(self):
        self.memory = DirectorMemoryLoader()
        self.prompt_engine = PromptEngine()


    def create_scene(self):
        
        character = self.memory.load_character("linfeng")

        world = self.memory.load_world("ancient-world")

        episode = self.memory.load_episode("ep001")


        scene = episode["scenes"][0]


        prompt = self.prompt_engine.create_scene_prompt(
            character,
            world,
            scene
        )


        return {
            "episode": episode["title"],
            "scene": scene["title"],
            "prompt": prompt
        }
