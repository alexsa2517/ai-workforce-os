import sys
import os

# เพิ่ม Path เพื่อให้เรียกใช้โมดูลใน app ได้
sys.path.append(os.path.join(os.getcwd(), "backend"))

from app.agents.director_ai.director import DirectorAI
from app.services.llm.openai_voice import OpenAIVoiceClient

def run_tts_example():
    print("--- AI Workforce OS: Voice Generation Example ---")
    
    try:
        # 1. เริ่มต้นระบบ DirectorAI และโหลดข้อมูลตัวละคร
        director = DirectorAI()
        character = director.memory.load_character("linhfeng")
        
        print(f"Character: {character['name']}")
        print(f"Role: {character['voice']['archetype']}")
        
        # 2. ข้อความที่ต้องการให้ตัวละครพูด (จำลองจากบทพูดใน Scene)
        dialogue_text = "ข้าคือหลินเฟิง ผู้ค้นหาความจริงในอดีต ประตูแห่งชะตากรรมกำลังจะเปิดออกแล้ว"
        
        # 3. เริ่มต้น Voice Client และสร้างเสียง
        print("\nGenerating speech using OpenAI TTS...")
        voice_client = OpenAIVoiceClient()
        
        # หมายเหตุ: โค้ดนี้ต้องการ OPENAI_API_KEY ใน .env เพื่อรันจริง
        # ในตัวอย่างนี้เราจะแสดง Logic การทำงาน
        result = voice_client.generate_speech(
            text=dialogue_text,
            character_voice_data=character['voice'],
            output_path="linhfeng_intro.mp3"
        )
        
        print(f"\nSuccess!")
        print(f"- Voice ID Selected: {result['voice_used']}")
        print(f"- Output saved to: {result['output_path']}")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Note: Make sure you have OPENAI_API_KEY in your .env file to run this for real.")

if __name__ == "__main__":
    run_tts_example()
