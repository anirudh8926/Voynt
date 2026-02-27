from __future__ import annotations

from typing import Any, Dict, List

from models import MonthPlan, RecommendedCard


def _find_card_by_id(card_id: str, cards: List[dict]) -> Dict[str, Any] | None:
    for c in cards:
        if str(c.get("id")) == str(card_id):
            return c
    return None


def build_monthly_plan(
    allocations,
    recommended_cards: List[RecommendedCard],
    cards: List[dict],
    profile: Dict[str, Any],
) -> List[MonthPlan]:
    monthly_plan: List[MonthPlan] = []

    for month in range(1, int(profile.get("timeline_months", 0) or 0) + 1):
        base_value = sum(float(a.expected_value_inr) for a in allocations)

        bonus_value = 0.0
        for rec in recommended_cards:
            if rec.action == "apply":
                card = _find_card_by_id(rec.card_id, cards)
                if card is None:
                    continue
                if month == int(card.get("welcome_months", 0) or 0):
                    bonus_value += float(rec.expected_bonus_value_inr or 0.0)

        monthly_plan.append(
            MonthPlan(
                month=month,
                allocations=list(allocations),
                total_expected_value_inr=round(float(base_value + bonus_value), 2),
            )
        )

    return monthly_plan

