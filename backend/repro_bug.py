import sys
import os
from pathlib import Path

# เพิ่ม backend/app เข้าไปใน sys.path เพื่อให้ import ได้
sys.path.append(os.path.join(os.getcwd(), "backend"))

print("--- Testing LLM Factory Import ---")
try:
    from app.services.llm.factory import LLMFactory
    print("LLMFactory imported successfully")
except Exception as e:
    print(f"Error importing LLMFactory: {e}")

print("\n--- Testing DirectorAI Knowledge Loading ---")
try:
    from app.agents.director_ai.director import DirectorAI
    director = DirectorAI()
    # เปลี่ยน directory ไปที่ root ของโปรเจกต์เพื่อให้ Path ใน memory_loader ทำงานได้ (ถ้า path ถูกต้อง)
    os.chdir(os.path.join(os.getcwd()))
    result = director.create_scene()
    print("DirectorAI create_scene success!")
except Exception as e:
    print(f"Error in DirectorAI: {e}")
