from app.services.llm.factory import LLMFactory


class DeveloperAI:
    """
    Developer AI Employee

    Responsibilities:
    - Understand development requests
    - Generate implementation plans
    - Generate code
    - Modify project files
    - Work with GitHub workflow
    """

    def __init__(self, provider="deepseek"):
        self.name = "Developer AI Employee #003"
        self.role = "AI Software Engineer"
        self.llm = LLMFactory.get(provider)

    def analyze(self, request: str):
        prompt = f"""
You are an expert AI Software Engineer.

Repository:
AI Workforce OS

User Request:
{request}

Return:
1. Goal
2. Files to create or modify
3. Implementation plan
"""

        return self.llm.generate(prompt)
