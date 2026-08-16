"""Manus API v2 operator adapter.

Used only after the board validates an opportunity. Manus can execute longer
agent tasks and can use authorized connectors configured in the Manus account.
"""
import os
from typing import Any, Dict, Optional
import requests
from app.core.config import settings


class ManusOperator:
    def __init__(self):
        self.api_key = settings.MANUS_API_KEY or os.getenv("MANUS_API_KEY", "")
        self.base_url = settings.MANUS_BASE_URL.rstrip("/")

    def create_task(self, message: str, project_id: Optional[str] = None,
                    connectors: Optional[list[str]] = None) -> Dict[str, Any]:
        if not self.api_key:
            return {"ok": False, "error": "api_key_missing", "detail": "MANUS_API_KEY is not configured."}
        payload: Dict[str, Any] = {"message": {"content": message}}
        if project_id:
            payload["project_id"] = project_id
        if connectors:
            payload["message"]["connectors"] = connectors
        try:
            response = requests.post(
                f"{self.base_url}/v2/task.create",
                headers={"x-manus-api-key": self.api_key, "content-type": "application/json"},
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            return {"ok": False, "error": "api_error", "detail": str(exc)}
