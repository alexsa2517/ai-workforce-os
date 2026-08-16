"""AI Money Lab orchestration primitives.

Coordinates specialist LLMs around a revenue-first business opportunity.
The system treats THB 1,000,000 monthly revenue as a minimum portfolio target,
not a ceiling.
"""
from __future__ import annotations

from typing import Any, Dict, List

from app.services.llm.factory import LLMFactory


TARGET_MONTHLY_REVENUE = 1_000_000

ROLES = {
    "ceo": "Act as CEO. Make the final strategic recommendation and prioritize actions.",
    "market": "Act as market intelligence. Identify demand, customers, competitors, pricing and risks.",
    "finance": "Act as finance/engineering analyst. Estimate economics, costs, margins, feasibility and required volume.",
    "critic": "Act as a skeptical investment committee member. Attack assumptions and identify failure modes.",
}


class MoneyLab:
    """Run a structured multi-model business evaluation."""

    def __init__(self) -> None:
        self.results: Dict[str, Dict[str, Any]] = {}

    def _ask(self, provider: str, role: str, brief: str) -> Dict[str, Any]:
        client = LLMFactory.get(provider)
        return client.generate(
            prompt=brief,
            system_prompt=ROLES[role],
            temperature=0.4,
            max_tokens=4000,
        )

    def evaluate(self, idea: str, budget_thb: float = 0, constraints: str = "") -> Dict[str, Any]:
        """Evaluate one business idea with multiple independent specialists."""
        context = (
            f"Business idea: {idea}\n"
            f"Available budget (THB): {budget_thb}\n"
            f"Constraints: {constraints}\n"
            f"Minimum monthly revenue requirement: THB {TARGET_MONTHLY_REVENUE:,}.\n"
            "Do not treat hypothetical market size as revenue. Distinguish assumptions from evidence."
        )

        # Current repository supports these three providers. Additional providers can
        # be added behind the same LLMFactory interface without changing this API.
        self.results["market"] = self._ask("gemini", "market", context)
        self.results["finance"] = self._ask("deepseek", "finance", context)

        evidence = "\n\n--- MARKET ---\n" + self.results["market"].get("content", "")
        evidence += "\n\n--- FINANCE ---\n" + self.results["finance"].get("content", "")
        self.results["critic"] = self._ask("deepseek", "critic", context + evidence)

        decision_prompt = (
            context
            + evidence
            + "\n\n--- CRITIC ---\n"
            + self.results["critic"].get("content", "")
            + "\n\nReturn a CEO decision using exactly these sections: VERDICT, REVENUE_PATH, "
              "KEY_ASSUMPTIONS, RISKS, NEXT_7_DAYS, SCALE_TRIGGER, KILL_TRIGGER. "
              "Verdict must be BUILD, TEST, or KILL."
        )
        self.results["ceo"] = self._ask("openai", "ceo", decision_prompt)

        return {
            "target_monthly_revenue_thb": TARGET_MONTHLY_REVENUE,
            "idea": idea,
            "roles": self.results,
        }

    @staticmethod
    def portfolio_summary(projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize portfolio revenue against the minimum target."""
        actual = sum(float(p.get("monthly_revenue_thb", 0) or 0) for p in projects)
        return {
            "minimum_monthly_revenue_thb": TARGET_MONTHLY_REVENUE,
            "actual_monthly_revenue_thb": actual,
            "gap_thb": max(TARGET_MONTHLY_REVENUE - actual, 0),
            "above_minimum": actual >= TARGET_MONTHLY_REVENUE,
            "projects": len(projects),
        }
