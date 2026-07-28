"""
LipSyncService — ระบบแปลง เสียง + ภาพตัวละคร → วิดีโอปากขยับ

รองรับ 4 วิธี:
  1. Hedra API (แนะนำ — ใช้ได้ทันที แค่ใส่ API Key)
  2. D-ID API (ทางเลือก)
  3. Gemini (ฟรี — ใช้ Google Gemini เพื่อวิเคราะห์เสียง)
  4. Simulated (สำหรับทดสอบโดยไม่ต้องใช้ API ภายนอก)
"""

import os
import time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class LipSyncService:
    """Service สำหรับสร้างวิดีโอ Lip-Sync จากภาพตัวละคร + เสียงพูด"""

    # ── providers ──────────────────────────────────────────────
    HEDRA_BASE_URL = "https://api.hedra.com/v1"
    DID_BASE_URL = "https://api.d-id.com"

    def __init__(self, provider: str = "hedra"):
        """
        Args:
            provider: ชื่อ provider — "hedra", "did", "gemini", หรือ "simulated"
        """
        self.provider = provider.lower()
        self._validate_api_key()

    # ────────────────────────────────────────────────────────────
    # Public API
    # ────────────────────────────────────────────────────────────
    def generate_lip_sync(
        self,
        image_path: str,
        audio_path: str,
        output_path: str = "output_lipsync.mp4",
        duration_hint: int | None = None,
    ) -> dict:
        """
        สร้างวิดีโอ Lip-Sync จากภาพตัวละคร + เสียงพูด

        Args:
            image_path:   path ไปยังไฟล์ภาพตัวละคร (.jpg / .png)
            audio_path:   path ไปยังไฟล์เสียงพูด (.mp3 / .wav)
            output_path:  path ที่จะบันทึกวิดีโอลง
            duration_hint: ความยาววิดีโอที่ต้องการ (วินาที) — optional

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

        # เลือก provider
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if self.provider == "hedra":
            return self._hedra_generate(image_path, audio_path, output_path, duration_hint)
        elif self.provider == "did":
            return self._did_generate(image_path, audio_path, output_path, duration_hint)
        elif self.provider == "gemini":
            return self._gemini_generate(image_path, audio_path, output_path, duration_hint)
        else:
            return self._simulated_generate(image_path, audio_path, output_path, duration_hint)

    # ────────────────────────────────────────────────────────────
    # Hedra Implementation
    # ────────────────────────────────────────────────────────────
    def _hedra_generate(self, image_path, audio_path, output_path, duration_hint):
        """สร้าง Lip-Sync ผ่าน Hedra API"""
        api_key = os.getenv("HEDRA_API_KEY", "")
        if not api_key:
            return {
                "status": "error",
                "message": "HEDRA_API_KEY not set. Set it in .env to use Hedra lip-sync.",
                "fallback": "use simulated provider for testing",
            }

        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

        try:
            # Step 1: Upload audio
            upload_url = f"{self.HEDRA_BASE_URL}/speech/upload"
            with open(audio_path, "rb") as f:
                resp = requests.post(upload_url, headers=headers, files={"file": f})
            if resp.status_code not in (200, 201):
                return {"status": "error", "message": f"Audio upload failed: {resp.text}"}
            audio_job_id = resp.json().get("job_id")

            # Step 2: Create generation task
            task_url = f"{self.HEDRA_BASE_URL}/generation_tasks"
            task_payload = {
                "audio_job_id": audio_job_id,
                "image_path": image_path,
                "duration": duration_hint or 10,
                "output_format": "mp4",
            }
            resp = requests.post(task_url, headers=headers, json=task_payload)
            if resp.status_code not in (200, 201):
                return {"status": "error", "message": f"Task creation failed: {resp.text}"}
            task_id = resp.json().get("task_id")

            # Step 3: Poll until done
            video_url = self._poll_task(task_id, headers)
            if not video_url:
                return {"status": "error", "message": "Task timed out or failed"}

            # Step 4: Download video
            resp = requests.get(video_url, timeout=60)
            with open(output_path, "wb") as f:
                f.write(resp.content)

            return {
                "status": "success",
                "output_path": str(output_path),
                "provider": "hedra",
                "task_id": task_id,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ────────────────────────────────────────────────────────────
    # D-ID Implementation
    # ────────────────────────────────────────────────────────────
    def _did_generate(self, image_path, audio_path, output_path, duration_hint):
        """สร้าง Lip-Sync ผ่าน D-ID API"""
        api_key = os.getenv("DID_API_KEY", "")
        if not api_key:
            return {
                "status": "error",
                "message": "DID_API_KEY not set. Set it in .env to use D-ID lip-sync.",
                "fallback": "use simulated provider for testing",
            }

        from base64 import b64encode

        headers = {
            "Authorization": f"Basic {b64encode(api_key.encode()).decode()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            # Step 1: Upload audio to D-ID
            with open(audio_path, "rb") as f:
                audio_b64 = b64encode(f.read()).decode()

            # Step 2: Create talk
            talk_payload = {
                "source_url": None,
                "audio_url": None,
                "audio": {"content": f"data:audio/wav;base64,{audio_b64}"},
                "config": {
                    "result_format": "mp4",
                    "fluent": True,
                    "pad_audio": True,
                },
                "driver_url": "bank://unified",
            }
            resp = requests.post(
                f"{self.DID_BASE_URL}/talks", headers=headers, json=talk_payload
            )
            if resp.status_code not in (200, 201):
                return {"status": "error", "message": f"Talk creation failed: {resp.text}"}
            talk_id = resp.json()["id"]

            # Step 3: Poll
            video_url = self._poll_did_talk(talk_id, headers)
            if not video_url:
                return {"status": "error", "message": "D-ID task timed out"}

            # Step 4: Download
            resp = requests.get(video_url, timeout=120)
            with open(output_path, "wb") as f:
                f.write(resp.content)

            return {
                "status": "success",
                "output_path": str(output_path),
                "provider": "did",
                "talk_id": talk_id,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ────────────────────────────────────────────────────────────
    # Gemini Implementation (Free)
    # ────────────────────────────────────────────────────────────
    def _gemini_generate(self, image_path, audio_path, output_path, duration_hint):
        """สร้าง Lip-Sync ผ่าน Gemini (ฟรี)"""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "status": "error",
                "message": "GOOGLE_API_KEY or GEMINI_API_KEY not set. Set it in .env to use Gemini lip-sync.",
                "fallback": "use simulated provider for testing",
            }

        try:
            from app.services.lip_sync.gemini_lip_sync import GeminiLipSyncProvider
            provider = GeminiLipSyncProvider()
            result = provider.generate_lip_sync(
                image_path=image_path,
                audio_path=audio_path,
                output_path=output_path,
                duration_hint=duration_hint,
            )
            return result
        except ImportError:
            return {
                "status": "error",
                "message": "google-generativeai not installed. Install with: pip install google-generativeai",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ────────────────────────────────────────────────────────────
    # Simulated (for testing without external API)
    # ────────────────────────────────────────────────────────────
    def _simulated_generate(self, image_path, audio_path, output_path, duration_hint):
        """
        สร้างวิดีโอจำลองโดยใช้ FFmpeg — รวมภาพนิ่ง + เสียงเป็นวิดีโอ
        ใช้สำหรับทดสอบ Pipeline โดยไม่ต้องพึ่ง API ภายนอก

        ใน production ให้แทนที่ด้วย Hedra/D-ID API จริง
        """
        try:
            import subprocess

            # ตรวจสอบ FFmpeg
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)

            # ใช้ FFmpeg รวมภาพ + เสียงเป็นวิดีโอ
            duration = duration_hint or 10
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", image_path,
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
                "provider": "simulated",
                "note": "This is a simulated lip-sync (image + audio merged). "
                        "Set HEDRA_API_KEY, DID_API_KEY, or GOOGLE_API_KEY for real lip-sync.",
            }
        except FileNotFoundError:
            return {
                "status": "error",
                "message": "FFmpeg not installed. Install with: sudo apt install ffmpeg",
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ────────────────────────────────────────────────────────────
    # Helper
    # ────────────────────────────────────────────────────────────
    def _validate_api_key(self):
        """ตรวจสอบว่ามี API Key ที่จำเป็นหรือไม่"""
        if self.provider == "hedra":
            key = os.getenv("HEDRA_API_KEY", "")
            if not key:
                pass  # จะแจ้ง error เมื่อเรียกใช้จริง
        elif self.provider == "did":
            key = os.getenv("DID_API_KEY", "")
            if not key:
                pass
        elif self.provider == "gemini":
            key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not key:
                pass

    def _poll_task(self, task_id, headers, max_wait=120):
        """Poll Hedra task จนกว่าจะเสร็จ"""
        deadline = time.time() + max_wait
        while time.time() < deadline:
            resp = requests.get(
                f"{self.HEDRA_BASE_URL}/generation_tasks/{task_id}",
                headers=headers,
            )
            data = resp.json()
            status = data.get("status", "")
            if status in ("completed", "done"):
                return data.get("video_url") or data.get("result_url")
            elif status in ("failed", "error"):
                return None
            time.sleep(3)
        return None

    def _poll_did_talk(self, talk_id, headers, max_wait=120):
        """Poll D-ID talk จนกว่าจะเสร็จ"""
        deadline = time.time() + max_wait
        while time.time() < deadline:
            resp = requests.get(
                f"{self.DID_BASE_URL}/talks/{talk_id}",
                headers=headers,
            )
            data = resp.json()
            status = data.get("status", "")
            if status == "done":
                return data.get("result_url")
            elif status == "error":
                return None
            time.sleep(5)
        return None
