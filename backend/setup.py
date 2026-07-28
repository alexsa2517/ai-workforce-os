"""
AI Workforce OS - Backend package setup
"""
from setuptools import setup, find_packages

setup(
    name="ai-workforce-os",
    version="0.2.0",
    description="AI Workforce OS - AI-powered workforce management system",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "fastapi>=0.115.0",
        "uvicorn[standard]>=0.30.0",
        "pydantic>=2.9.0",
        "pydantic-settings>=2.6.0",
        "python-dotenv>=1.0.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "openai>=1.48.0",
        "google-generativeai>=0.8.0",
        "PyJWT>=2.9.0",
        "passlib[bcrypt]>=1.7.4",
        "requests>=2.32.0",
        "Pillow>=10.0.0",
        "python-multipart>=0.0.9",
        "httpx>=0.27.0",
        "prometheus-client>=0.21.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-workforce=app.main:app",
        ],
    },
)
