from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.money_lab import MoneyLab, TARGET_MONTHLY_REVENUE

router = APIRouter(prefix="/api/v1/money-lab", tags=["AI Money Lab"])

class OpportunityRequest(BaseModel):
    idea: str = Field(..., min_length=3, max_length=10000)
    budget_thb: float = Field(default=0, ge=0)
    constraints: str = Field(default="", max_length=10000)

class PortfolioProject(BaseModel):
    monthly_revenue_thb: float = Field(default=0, ge=0)

@router.get("/target")
async def target():
    return {"minimum_monthly_revenue_thb": TARGET_MONTHLY_REVENUE, "maximum_monthly_revenue_thb": None, "rule": "Revenue above 1M remains a growth target."}

@router.post("/evaluate")
async def evaluate(request: OpportunityRequest):
    try:
        return MoneyLab().evaluate(request.idea, request.budget_thb, request.constraints)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@router.post("/portfolio")
async def portfolio(projects: list[PortfolioProject]):
    return MoneyLab.portfolio_summary([p.model_dump() for p in projects])
