import sys
import os

sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.agents.director_ai.director import DirectorAI
from app.services.llm.gemini_media import GeminiMediaService

def run_multimedia_workflow():
    print("--- AI Workforce OS: Gemini Multimedia Workflow ---")
    
    try:
        # 1. สร้างเนื้อหาและรายละเอียดตัวละคร
        director = DirectorAI()
        scene_data = director.create_scene()
        character = director.memory.load_character("linhfeng")
        
        print(f"\n[1] Scene Created: {scene_data['scene']}")
        print(f"Character: {character['name']} with Natural Facial Dynamics")
        
        # 2. เริ่มต้น Gemini Media Service
        media_service = GeminiMediaService()
        
        # 3. สร้างภาพตัวละคร (Image Generation)
        print("\n[2] Requesting Image Generation from Gemini/Imagen...")
        image_result = media_service.generate_image(
            prompt=scene_data['prompt'],
            aspect_ratio="9:16" # ตามความชอบของผู้ใช้
        )
        print(f"Result: {image_result['status']}")
        
        # 4. สร้างวิดีโอ (Video Generation)
        print("\n[3] Requesting Video Generation (Lip-Sync/Veo) from Gemini...")
        video_result = media_service.generate_video(
            image_prompt=scene_data['prompt'],
            audio_context=character['voice']['tone']
        )
        print(f"Result: {video_result['status']}")
        print(f"Message: {video_result.get('details', 'In progress')}")

    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    run_multimedia_workflow()
