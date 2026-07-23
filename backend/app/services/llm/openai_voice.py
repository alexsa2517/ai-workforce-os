import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from ..voice_service import VoiceService

load_dotenv()

class OpenAIVoiceClient:
    """Client สำหรับเชื่อมต่อกับ OpenAI Text-to-Speech (TTS)"""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def generate_speech(self, text, character_voice_data, output_path="output.mp3"):
        """
        แปลงข้อความเป็นเสียงโดยใช้ Voice ID ที่เลือกอัตโนมัติ
        """
        # 1. เลือก Voice ID อัตโนมัติผ่าน VoiceService
        voice_id = VoiceService.select_voice(character_voice_data, provider="openai")
        
        # 2. ดึงคำแนะนำด้านความเร็ว (Speed)
        speed = character_voice_data.get("speed", 1.0)

        # 3. เรียก OpenAI TTS API
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice_id,
            input=text,
            speed=speed
        )

        # 4. บันทึกไฟล์เสียง
        response.stream_to_file(output_path)
        
        return {
            "voice_used": voice_id,
            "output_path": output_path,
            "status": "success"
        }
