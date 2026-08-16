from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.manus_operator import ManusOperator

router = APIRouter(prefix="/api/v1/operator", tags=["Operator"])

class OperatorRequest(BaseModel):
    message: str = Field(..., min_length=10, max_length=30000)
    project_id: str | None = None
    connectors: list[str] | None = None

@router.post("/manus/task")
async def create_manus_task(request: OperatorRequest):
    result = ManusOperator().create_task(request.message, request.project_id, request.connectors)
    if result.get("error") == "api_key_missing":
        raise HTTPException(status_code=503, detail=result["detail"])
    return result
