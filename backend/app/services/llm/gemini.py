import os

import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()


class GeminiClient:

    def __init__(self):

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel("gemini-1.5-pro")


    def generate(self, prompt: str):

        response = self.model.generate_content(prompt)

        return response.text
