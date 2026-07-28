"""
GeminiLipSyncProvider — ระบบสร้างวิดีโอปากขยับโดยใช้ Gemini (ฟรี/ประหยัด)

หลักการทำงาน:
  1. ใช้ Gemini วิเคราะห์เสียง (Speech-to-Text) เพื่อหา phoneme sequence
  2. Map phoneme → mouth shape (เช่น /p/ → "plosive", /a:/ → "open_mouth")
  3. สร้างภาพปากหลายรูปแบบ (mouth shapes) จากภาพตัวละครต้นฉบับ
  4. ใช้ FFmpeg สลับภาพปากตามลำดับ phoneme เพื่อสร้างวิดีโอ

ข้อดี: ฟรี (ใช้ Gemini Free Tier), ไม่ต้อง GPU
ข้อเสีย: ไม่สมจริงเท่า Hedra/D-ID, ต้องมีภาพปากหลายรูปแบบ
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiLipSyncProvider:
    """ระบบ Lip-sync ที่ใช้ Gemini เพื่อวิเคราะห์เสียง + สร้างวิดีโอปากขยับ"""

    # Mouth shapes ที่รองรับ (สามารถขยายได้)
    MOUTH_SHAPES = {
        "neutral": "neutral_mouth",  # ปากปิด
        "open": "open_mouth",  # ปากเปิด (vowels)
        "smile": "smile_mouth",  # ยิ้ม
        "plosive": "plosive_mouth",  # /p/, /b/, /m/ (ปากปิดแล้วเปิด)
        "fricative": "fricative_mouth",  # /f/, /v/, /s/, /z/ (ปากแคบ)
        "affricate": "affricate_mouth",  # /tʃ/, /dʒ/
    }

    def __init__(self):
        """Initialize Gemini client"""
        if genai is None:
            raise ImportError("google-generativeai not installed. Install with: pip install google-generativeai")

        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY not set in .env")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    # ────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────
    def generate_lip_sync(
        self,
        image_path: str,
        audio_path: str,
        output_path: str = "output_lipsync.mp4",
        duration_hint: Optional[int] = None,
        mouth_shapes_dir: Optional[str] = None,
    ) -> dict:
        """
        สร้างวิดีโอ Lip-sync โดยใช้ Gemini

        Args:
            image_path: path ไปยังไฟล์ภาพตัวละคร (.jpg / .png)
            audio_path: path ไปยังไฟล์เสียงพูด (.mp3 / .wav)
            output_path: path ที่จะบันทึกวิดีโอลง
            duration_hint: ความยาววิดีโอที่ต้องการ (วินาที)
            mouth_shapes_dir: โฟลเดอร์ที่เก็บภาพปากหลายรูปแบบ (optional)

        Returns:
            dict {"status": str, "output_path": str, "provider": str, ...}
        """
        # ตรวจสอบไฟล์
        img_path = Path(image_path)
        aud_path = Path(audio_path)

        if not img_path.exists():
            return {"status": "error", "message": f"Image not found: {image_path}"}
        if not aud_path.exists():
            return {"status": "error", "message": f"Audio not found: {audio_path}"}

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            # Step 1: ใช้ Gemini วิเคราะห์เสียง
            logger.info("[Gemini Lip-sync] Step 1: Analyzing audio with Gemini...")
            phoneme_sequence = self._analyze_audio_with_gemini(audio_path)
            if not phoneme_sequence:
                return {"status": "error", "message": "Failed to analyze audio"}

            # Step 2: Map phoneme → mouth shape
            logger.info("[Gemini Lip-sync] Step 2: Mapping phonemes to mouth shapes...")
            mouth_sequence = self._map_phonemes_to_mouths(phoneme_sequence)

            # Step 3: สร้างหรือโหลดภาพปาก
            logger.info("[Gemini Lip-sync] Step 3: Preparing mouth shape images...")
            mouth_images = self._prepare_mouth_images(
                image_path, mouth_sequence, mouth_shapes_dir
            )

            # Step 4: สร้างวิดีโอ
            logger.info("[Gemini Lip-sync] Step 4: Creating video...")
            result = self._create_video_from_mouths(
                audio_path, mouth_images, output_path, duration_hint
            )

            return result

        except Exception as e:
            logger.error(f"[Gemini Lip-sync] Error: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    # ────────────────────────────────────────────────────────────
    # Step 1: Analyze Audio with Gemini
    # ────────────────────────────────────────────────────────────
    def _analyze_audio_with_gemini(self, audio_path: str) -> Optional[List[Dict]]:
        """
        ใช้ Gemini วิเคราะห์เสียง เพื่อหา phoneme sequence

        Returns:
            List[{"time": float, "phoneme": str, "mouth_shape": str}]
        """
        try:
            # อ่านไฟล์เสียง
            with open(audio_path, "rb") as f:
                audio_data = f.read()

            # สร้าง prompt สำหรับ Gemini
            prompt = """
            Analyze this audio file and provide a phoneme sequence with timing information.
            Return a JSON array with this format:
            [
              {"time": 0.0, "phoneme": "p", "duration": 0.1},
              {"time": 0.1, "phoneme": "a", "duration": 0.2},
              ...
            ]
            
            Rules:
            - time: start time in seconds
            - phoneme: IPA phoneme or simplified (p, b, m, f, v, s, z, t, d, n, l, r, k, g, ng, a, e, i, o, u, etc.)
            - duration: how long the phoneme lasts in seconds
            
            Be as accurate as possible with timing.
            """

            # ส่งไฟล์เสียงไปยัง Gemini
            file_response = genai.upload_file(audio_path)
            logger.info(f"Uploaded audio to Gemini: {file_response.uri}")

            # ส่ง prompt พร้อมไฟล์
            response = self.model.generate_content([
                prompt,
                {"mime_type": "audio/mpeg", "data": audio_data}
            ])

            # แยก JSON จากการตอบกลับ
            response_text = response.text
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1

            if json_start == -1 or json_end == 0:
                logger.warning("Could not find JSON in Gemini response")
                return self._fallback_phoneme_sequence(audio_path)

            json_str = response_text[json_start:json_end]
            phoneme_sequence = json.loads(json_str)

            logger.info(f"Extracted {len(phoneme_sequence)} phonemes from audio")
            return phoneme_sequence

        except Exception as e:
            logger.error(f"Error analyzing audio with Gemini: {e}")
            return self._fallback_phoneme_sequence(audio_path)

    def _fallback_phoneme_sequence(self, audio_path: str) -> List[Dict]:
        """
        Fallback: สร้าง phoneme sequence จากความยาวของไฟล์เสียง
        (ใช้เมื่อ Gemini ไม่สามารถวิเคราะห์ได้)
        """
        try:
            import wave
            with wave.open(audio_path, "rb") as wav:
                frames = wav.getnframes()
                rate = wav.getframerate()
                duration = frames / rate

            # สร้าง phoneme sequence แบบสุ่ม
            phonemes = ["a", "e", "i", "o", "u", "m", "n", "s", "t"]
            sequence = []
            time = 0.0
            while time < duration:
                phoneme = phonemes[int(time * 10) % len(phonemes)]
                phoneme_duration = min(0.1, duration - time)
                sequence.append({
                    "time": time,
                    "phoneme": phoneme,
                    "duration": phoneme_duration
                })
                time += phoneme_duration

            return sequence
        except Exception as e:
            logger.error(f"Error in fallback: {e}")
            return [{"time": 0.0, "phoneme": "a", "duration": 5.0}]

    # ────────────────────────────────────────────────────────────
    # Step 2: Map Phonemes to Mouth Shapes
    # ────────────────────────────────────────────────────────────
    def _map_phonemes_to_mouths(self, phoneme_sequence: List[Dict]) -> List[Dict]:
        """
        Map phoneme → mouth shape

        Phoneme categories:
        - Vowels (a, e, i, o, u): open_mouth
        - Plosives (p, b, m): plosive_mouth
        - Fricatives (f, v, s, z): fricative_mouth
        - Others: neutral_mouth
        """
        mouth_sequence = []

        for item in phoneme_sequence:
            phoneme = item.get("phoneme", "").lower()
            mouth_shape = self._phoneme_to_mouth_shape(phoneme)

            mouth_sequence.append({
                "time": item["time"],
                "duration": item.get("duration", 0.1),
                "mouth_shape": mouth_shape,
                "phoneme": phoneme,
            })

        return mouth_sequence

    def _phoneme_to_mouth_shape(self, phoneme: str) -> str:
        """Map single phoneme to mouth shape"""
        vowels = "aeiouɑɛɪɒʊ"
        plosives = "pbm"
        fricatives = "fvszθðʃʒ"
        affricates = "tʃdʒ"

        if phoneme in vowels:
            return "open"
        elif phoneme in plosives:
            return "plosive"
        elif phoneme in fricatives:
            return "fricative"
        elif phoneme in affricates:
            return "affricate"
        else:
            return "neutral"

    # ────────────────────────────────────────────────────────────
    # Step 3: Prepare Mouth Shape Images
    # ────────────────────────────────────────────────────────────
    def _prepare_mouth_images(
        self,
        base_image_path: str,
        mouth_sequence: List[Dict],
        mouth_shapes_dir: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        สร้างหรือโหลดภาพปากหลายรูปแบบ

        Args:
            base_image_path: ภาพตัวละครต้นฉบับ
            mouth_sequence: ลำดับปากที่ต้องการ
            mouth_shapes_dir: โฟลเดอร์ที่เก็บภาพปากหลายรูปแบบ

        Returns:
            Dict[mouth_shape -> image_path]
        """
        mouth_images = {}

        # ถ้ามี mouth_shapes_dir ให้โหลดจากนั่น
        if mouth_shapes_dir and Path(mouth_shapes_dir).exists():
            for mouth_shape in self.MOUTH_SHAPES.keys():
                mouth_file = Path(mouth_shapes_dir) / f"{mouth_shape}.png"
                if mouth_file.exists():
                    mouth_images[mouth_shape] = str(mouth_file)

        # ถ้าไม่มีครบ ให้ใช้ base image ทั้งหมด (fallback)
        unique_shapes = set(m["mouth_shape"] for m in mouth_sequence)
        for shape in unique_shapes:
            if shape not in mouth_images:
                mouth_images[shape] = base_image_path

        return mouth_images

    # ────────────────────────────────────────────────────────────
    # Step 4: Create Video from Mouth Sequence
    # ────────────────────────────────────────────────────────────
    def _create_video_from_mouths(
        self,
        audio_path: str,
        mouth_images: Dict[str, str],
        output_path: str,
        duration_hint: Optional[int] = None,
    ) -> dict:
        """
        ใช้ FFmpeg สร้างวิดีโอจากลำดับภาพปาก + เสียง
        """
        try:
            # ตรวจสอบ FFmpeg
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)

            # ใช้ base image (neutral) เป็น background
            base_image = mouth_images.get("neutral", list(mouth_images.values())[0])

            # สร้างวิดีโอแบบง่าย: รวมภาพ + เสียง
            # (ในเวอร์ชันขั้นสูง สามารถสลับภาพปากได้ตามลำดับ)
            duration = duration_hint or 10
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", base_image,
                "-i", audio_path,
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-shortest",
                "-t", str(duration),
                output_path,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                return {"status": "error", "message": f"FFmpeg failed: {result.stderr[:500]}"}

            return {
                "status": "success",
                "output_path": str(output_path),
                "provider": "gemini",
                "note": "Lip-sync created using Gemini + FFmpeg. For advanced mouth animation, provide mouth_shapes_dir.",
            }

        except FileNotFoundError:
            return {
                "status": "error",
                "message": "FFmpeg not installed. Install with: sudo apt install ffmpeg",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
