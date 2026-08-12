import json
from openai import OpenAI

from app.core.config import settings
from app.services.production.schemas import ProductionPlan

SYSTEM_PROMPT = """You are the AI Director for a cinematic Thai-language production system.
Return JSON only. Create a production plan with a character bible and scenes/shots.
Every shot must specify camera, duration, characters, dialogue, performance, lighting and reflections.
Prioritize natural Thai dialogue, clear Thai pronunciation, realistic lip-sync readiness,
natural blinking/eye movement, facial expressions, body language, physically plausible lighting,
and realistic eye/object reflections. Keep character attributes identical across all scenes.
For conversations in one scene, keep both characters present and specify who speaks each line.
"""


class DeepSeekDirector:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )

    def create_plan(self, idea: str) -> ProductionPlan:
        if not settings.DEEPSEEK_API_KEY:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")

        response = self.client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Create a JSON production plan for this idea. "
                        "Use Thai for story/dialogue fields and keep the schema explicit.\n"
                        f"IDEA: {idea}"
                    ),
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=12000,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("DeepSeek returned empty JSON")
        return ProductionPlan.model_validate(json.loads(content))
