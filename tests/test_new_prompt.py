import sys
import os

# Add backend/app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.agents.director_ai.memory_loader import DirectorMemoryLoader
from app.agents.director_ai.prompt_engine import PromptEngine

def test_prompt():
    loader = DirectorMemoryLoader()
    engine = PromptEngine()

    # Mock data for world and scene
    world = {"description": "อาณาจักรโบราณที่เต็มไปด้วยหมอกหนาและแสงจันทร์"}
    scene = {
        "title": "การเผชิญหน้าในหมอก",
        "action": "หลินเฟิงยืนนิ่งท่ามกลางหมอก ค่อยๆ ชักดาบออกมาอย่างช้าๆ",
        "emotion": "ตึงเครียดและเด็ดเดี่ยว"
    }

    try:
        character = loader.load_character("linhfeng")
        prompt = engine.create_scene_prompt(character, world, scene)
        
        print("--- Generated Prompt with Natural Expressions ---")
        print(prompt)
        print("-------------------------------------------------")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_prompt()
