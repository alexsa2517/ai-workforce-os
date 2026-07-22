import os

from google import genai
from dotenv import load_dotenv


load_dotenv()


class GeminiClient:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )


    def generate(self, prompt: str):

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )

        return response.text
