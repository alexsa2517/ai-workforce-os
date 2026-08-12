import time
from pathlib import Path

from app.core.config import settings


class GoogleMediaProvider:
    """Google Gemini/Veo provider.

    Real media generation is intentionally opt-in. The quality-gate caller must
    approve the production plan before this provider is invoked.
    """

    def __init__(self) -> None:
        if not settings.GOOGLE_API_KEY:
            raise RuntimeError("GOOGLE_API_KEY is not configured")
        from google import genai

        self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)

    def generate_video(self, prompt: str, output_path: str, aspect_ratio: str = "9:16") -> str:
        """Generate an 8-second video with Veo 3.1 and save it locally."""
        operation = self.client.models.generate_videos(
            model=settings.GOOGLE_VIDEO_MODEL,
            prompt=prompt,
            config={"aspect_ratio": aspect_ratio},
        )
        while not operation.done:
            time.sleep(10)
            operation = self.client.operations.get(operation)

        generated = operation.response.generated_videos[0]
        self.client.files.download(file=generated.video)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        generated.video.save(str(path))
        return str(path)
