from fastapi import FastAPI

app = FastAPI(
    title="AI Workforce OS",
    version="0.1.0"
)

from app.services.llm.factory import LLMFactory
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = "openai"

@app.get("/")
def root():
    return {
        "message": "AI Workforce OS is running",
        "employee": "Sales AI Employee #001",
        "version": "0.1.0"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        llm = LLMFactory.get(request.provider)
        response = llm.generate(request.message)
        return {
            "provider": request.provider,
            "response": response
        }
    except Exception as e:
        return {"error": str(e)}
