"""AI Money Lab orchestration.

Coordinates independent AI providers as a virtual venture team. The service is
provider-agnostic: each specialist receives the same business brief, then the
CEO stage synthesizes the specialist reports into a ranked decision.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List

from app.services.llm.factory import LLMFactory

logger = logging.getLogger("ai_workforce.ai_money_lab")

SPECIALIST_PROMPTS: Dict[str, str] = {
    "research": "Act as a market researcher. Find demand, customer pain, competitors, trends, and evidence needed to validate this business. Be skeptical and distinguish facts from assumptions.",
    "business": "Act as a business strategist. Turn the idea into a concrete offer, target customer, acquisition channel, pricing model, and simple path to first revenue.",
    "finance": "Act as a finance operator. Estimate startup cost, monthly operating cost, gross margin, break-even logic, and realistic revenue scenarios. State assumptions clearly.",
    "technology": "Act as a CTO. Decide the simplest technical architecture and which existing AI/services can build the MVP. Identify integration risks and avoid unnecessary engineering.",
    "critic": "Act as a hostile investment committee member. Try to kill this idea. Identify market, execution, legal, technical, distribution, and unit-economic risks. Then state what evidence would change your mind.",
}

PROVIDER_BY_ROLE = {
    "research": "gemini",
    "business": "openai",
    "finance": "deepseek",
    "technology": "deepseek",
    "critic": "kimi",
}


def _run(provider: str, prompt: str, system: str) -> Dict[str, Any]:
    """Run one provider without letting a single failure stop the board."""
    try:
        client = LLMFactory.get(provider)
        result = client.generate(
            prompt=prompt,
            system_prompt=system,
            temperature=0.4,
            max_tokens=5000,
        )
        return {
            "provider": provider,
            "content": result.get("content", ""),
            "usage": result.get("usage", {}),
            "error": result.get("error"),
            "detail": result.get("detail"),
        }
    except Exception as exc:  # pragma: no cover - defensive boundary
        logger.exception("Money Lab provider failed: %s", provider)
        return {"provider": provider, "content": "", "error": "provider_failed", "detail": str(exc)}


async def run_money_lab(brief: str, goal: str = "Find the best realistic path to revenue") -> Dict[str, Any]:
    """Run the V1 AI Money Lab board and return auditable specialist reports."""
    context = f"BUSINESS BRIEF:\n{brief}\n\nPRIMARY GOAL:\n{goal}"
    tasks = []
    roles: List[str] = list(SPECIALIST_PROMPTS.keys())

    for role in roles:
        provider = PROVIDER_BY_ROLE[role]
        prompt = f"{context}\n\nYou are the {role.upper()} specialist. Return a concise report with findings, assumptions, and a recommendation."
        tasks.append(asyncio.to_thread(_run, provider, prompt, SPECIALIST_PROMPTS[role]))

    reports = await asyncio.gather(*tasks)
    successful = [r for r in reports if r.get("content")]

    dossier = "\n\n".join(
        f"=== {roles[i].upper()} ({reports[i]['provider']}) ===\n{reports[i].get('content','NO REPORT')}"
        for i in range(len(reports))
    )

    ceo_prompt = f"""{context}

You are the AI Venture CEO. Below are independent specialist reports.

{dossier}

Synthesize them. Do not blindly average opinions. Produce:
1. FINAL VERDICT: GO / TEST / NO-GO
2. Opportunity score 0-100
3. Why this can make money
4. Biggest reasons it may fail
5. The cheapest 7-day validation experiment
6. First offer and target customer
7. Estimated first-revenue path
8. Three concrete next actions
9. What evidence is still missing

Return valid JSON with keys: verdict, score, thesis, risks, validation, offer, revenue_path, next_actions, missing_evidence."""

    ceo_provider = "openai"
    ceo = await asyncio.to_thread(_run, ceo_provider, ceo_prompt, "You are a disciplined venture studio CEO. Prefer evidence, small experiments, and real revenue over hype.")

    decision: Any = ceo.get("content", "")
    try:
        decision = json.loads(decision)
    except (TypeError, json.JSONDecodeError):
        pass

    return {
        "goal": goal,
        "specialists": reports,
        "successful_specialists": len(successful),
        "decision": decision,
        "architecture": "parallel specialist board -> CEO synthesis",
    }
