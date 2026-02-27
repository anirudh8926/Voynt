from typing import List

from models import (
    CardAllocation,
    MonthPlan,
    RecommendedCard,
    StrategyPlan,
    UserProfile,
)


def run_agent2(profile: UserProfile, cards: List[dict]) -> StrategyPlan:
    """
    Multi-layer reward strategy optimizer.

    This is a placeholder implementation to satisfy the pipeline contract.
    It creates a simple plan that allocates the full monthly spend to the
    first available card (if any) with zeroed reward metrics.
    """
    monthly_plan: List[MonthPlan] = []

    if cards:
        primary_card = cards[0]
        card_id = str(primary_card.get("id", "card_1"))
        card_name = str(primary_card.get("name", "Primary Card"))
    else:
        card_id = "card_1"
        card_name = "Generic Rewards Card"

    for month in range(1, profile.timeline_months + 1):
        allocation = CardAllocation(
            card_id=card_id,
            card_name=card_name,
            category="other",
            amount_inr=profile.monthly_spend_inr,
            expected_pts=0.0,
            expected_value_inr=0.0,
        )
        month_plan = MonthPlan(
            month=month,
            allocations=[allocation],
            total_expected_value_inr=allocation.expected_value_inr,
        )
        monthly_plan.append(month_plan)

    recommended_cards: List[RecommendedCard] = [
        RecommendedCard(
            card_id=card_id,
            card_name=card_name,
            action="apply",
            reason="Placeholder strategy — real optimizer not yet implemented.",
            approval_prob=float(
                cards[0].get("approval_prob", 0.8) if cards else 0.8
            ),
            expected_bonus_value_inr=0.0,
        )
    ]

    total_rewards_inr = 0.0
    total_fees_inr = 0.0
    net_value_inr = total_rewards_inr - total_fees_inr

    return StrategyPlan(
        session_id=profile.session_id,
        monthly_plan=monthly_plan,
        recommended_cards=recommended_cards,
        total_rewards_inr=total_rewards_inr,
        total_fees_inr=total_fees_inr,
        net_value_inr=net_value_inr,
    )

