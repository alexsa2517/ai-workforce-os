class VoiceService:
    """Service สำหรับจัดการการเลือกเสียง AI อัตโนมัติ"""

    # ตัวอย่าง Voice Mapping สำหรับ OpenAI TTS หรือ ElevenLabs
    VOICE_MODELS = {
        "openai": {
            "male": {
                "hero": "alloy",
                "villain": "onyx",
                "young-adult": "echo",
                "elder": "fable"
            },
            "female": {
                "hero": "shimmer",
                "villain": "nova",
                "young-adult": "nova",
                "child": "alloy"
            }
        }
    }

    @staticmethod
    def select_voice(character_voice_data, provider="openai"):
        """เลือก Voice ID ที่เหมาะสมที่สุดตามข้อมูลตัวละคร"""
        gender = character_voice_data.get("gender", "male")
        archetype = character_voice_data.get("archetype", "hero")
        age_bracket = character_voice_data.get("age_bracket", "young-adult")

        provider_voices = VoiceService.VOICE_MODELS.get(provider, {})
        gender_voices = provider_voices.get(gender, {})

        # ลำดับการเลือก: Archetype -> Age Bracket -> Default
        voice_id = gender_voices.get(archetype) or gender_voices.get(age_bracket) or "alloy"
        
        return voice_id

    @staticmethod
    def get_speech_instructions(voice_data):
        """สร้างคำแนะนำสำหรับการพากย์เสียง"""
        traits = ", ".join(voice_data.get("vocal_traits", []))
        return {
            "pitch": voice_data.get("pitch", "medium"),
            "speed": voice_data.get("speed", 1.0),
            "instructions": f"Tone: {voice_data.get('tone')}. Traits: {traits}. Age: {voice_data.get('age_years')} years old."
        }
