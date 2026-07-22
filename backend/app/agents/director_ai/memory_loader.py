import json
from pathlib import Path


BASE_PATH = Path("knowledge/director-ai")


class DirectorMemoryLoader:

    def load_json(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)


    def load_character(self, character_name):
        path = BASE_PATH / "characters" / f"{character_name}.json"
        return self.load_json(path)


    def load_world(self, world_name):
        path = BASE_PATH / "worlds" / f"{world_name}.json"
        return self.load_json(path)


    def load_story(self, story_name):
        path = BASE_PATH / "stories" / f"{story_name}.json"
        return self.load_json(path)


    def load_episode(self, episode_name):
        path = BASE_PATH / "episodes" / f"{episode_name}.json"
        return self.load_json(path)
