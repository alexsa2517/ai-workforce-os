"""AI Money Lab API."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_money_lab import run_money_lab

router = APIRouter(prefix="/api/v1/money-lab", tags=["AI Money Lab"])


class MoneyLabRequest(BaseModel):
    brief: str = Field(..., min_length=10, max_length=30000)
    goal: str = Field(default="Find the best realistic path to revenue", max_length=2000)


@router.post("/run")
async def run(request: MoneyLabRequest):
    """Run a multi-model venture board against a business brief."""
    try:
        return await run_money_lab(request.brief, request.goal)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Money Lab failed: {exc}") from exc


@router.get("/team")
async def team():
    """Describe the default AI Money Lab team and routing."""
    return {
        "name": "AI Money Lab",
        "roles": [
            {"role": "CEO", "provider": "openai", "purpose": "synthesize and decide"},
            {"role": "Research", "provider": "gemini", "purpose": "market and demand"},
            {"role": "Business", "provider": "openai", "purpose": "offer and go-to-market"},
            {"role": "Finance", "provider": "deepseek", "purpose": "unit economics"},
            {"role": "Technology", "provider": "deepseek", "purpose": "MVP architecture"},
            {"role": "Critic", "provider": "kimi", "purpose": "red-team the idea"},
            {"role": "Operator", "provider": "manus", "purpose": "execute validated tasks (next integration)"},
        ],
        "flow": "brief -> parallel board -> CEO synthesis -> validation -> operator",
    }
