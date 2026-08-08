"""
Image Generation Service - DALL-E 3 Integration
Generates reference images and keyframes for video production.
"""
import logging
import os
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from openai import AsyncOpenAI, APITimeoutError, APIError

from app.core.config import settings

logger = logging.getLogger("ai_workforce.llm.image")

# Cost per image (approximate)
IMAGE_COSTS = {
    "dall-e-3": {"1024x1024": 0.04, "1024x1792": 0.08, "1792x1024": 0.08},
    "dall-e-2": {"1024x1024": 0.02, "512x512": 0.018, "256x256": 0.016},
}


class ImageGenerationService:
    """Async image generation using DALL-E 3."""

    def __init__(self):
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        self._has_api_key = bool(api_key)

        effective_key = api_key or "sk-no-openai-api-key-set"

        self.client = AsyncOpenAI(
            api_key=effective_key,
            timeout=60.0,
            max_retries=2,
        )
        self.output_dir = Path(settings.MOVIES_DIR) / "images"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def is_available(self) -> bool:
        return self._has_api_key

    async def generate(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        style: str = "vivid",
        n: int = 1,
    ) -> Dict[str, Any]:
        """Generate image(s) using DALL-E."""
        if not self._has_api_key:
            return {
                "urls": [],
                "local_paths": [],
                "revised_prompt": "",
                "error": "api_key_missing",
                "detail": "OPENAI_API_KEY is not configured.",
            }

        try:
            logger.info(f"Generating image: model={model}, size={size}, quality={quality}")

            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,  # type: ignore
                quality=quality,  # type: ignore
                style=style,  # type: ignore
                n=n,
                response_format="url",
            )

            urls = []
            local_paths = []
            revised_prompt = ""

            for image_data in response.data:
                if image_data.url:
                    urls.append(image_data.url)
                    local_path = await self._download_image(
                        image_data.url,
                        prefix=f"img_{uuid.uuid4().hex[:8]}",
                    )
                    local_paths.append(local_path)

                if image_data.revised_prompt:
                    revised_prompt = image_data.revised_prompt

            cost = IMAGE_COSTS.get(model, {}).get(size, 0.04) * n

            return {
                "urls": urls,
                "local_paths": local_paths,
                "revised_prompt": revised_prompt,
                "cost_usd": cost,
                "model": model,
                "size": size,
            }

        except APITimeoutError as e:
            logger.error(f"Image generation timeout: {e}")
            raise
        except APIError as e:
            logger.error(f"Image generation API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    async def _download_image(self, url: str, prefix: str = "img") -> str:
        """Download image from URL and save locally."""
        import httpx

        filename = f"{prefix}_{uuid.uuid4().hex[:6]}.png"
        filepath = self.output_dir / filename

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            filepath.write_bytes(response.content)

        logger.info(f"Image saved: {filepath}")
        return str(filepath)


# Global instance
image_service = ImageGenerationService()
