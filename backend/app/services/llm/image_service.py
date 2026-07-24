import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class ImageService:
    """Service สำหรับจัดการการสร้างภาพด้วย AI"""

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def generate_character_image(self, visual_prompt, size="1024x1024", quality="standard"):
        """
        สร้างภาพตัวละครโดยใช้ DALL-E 3
        """
        try:
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=visual_prompt,
                size=size,
                quality=quality,
                n=1,
            )

            image_url = response.data[0].url
            return {
                "status": "success",
                "url": image_url,
                "revised_prompt": response.data[0].revised_prompt
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
