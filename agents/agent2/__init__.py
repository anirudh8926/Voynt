from __future__ import annotations

import sys
from typing import Any, Dict, List

from .reward_matrix import build_cap_matrix, build_eligibility_mask, build_reward_matrix
from .allocator import greedy_allocate
from .welcome_bonus import evaluate_welcome_bonuses
from .timeline import build_monthly_plan
from models import StrategyPlan, UserProfile


def run_agent2(profile: dict, cards: list[dict]) -> StrategyPlan:
    # Never mutate input profile/cards
    if isinstance(profile, UserProfile):
        profile_dict: Dict[str, Any] = profile.model_dump()
    else:
        profile_dict = dict(profile)

    cards_list: List[dict] = list(cards)

    # Step 1: Build matrices
    matrix = build_reward_matrix(cards_list, profile_dict)
    cap_matrix = build_cap_matrix(cards_list)
    mask = build_eligibility_mask(cards_list, profile_dict)

    # Step 2: Greedy allocation for one base month
    allocations = greedy_allocate(cards_list, profile_dict, matrix, cap_matrix, mask)

    # Step 3: Evaluate welcome bonuses
    allocated_ids = {a.card_id for a in allocations}
    recommended = evaluate_welcome_bonuses(cards_list, profile_dict, allocated_ids)

    # Step 4: Project across timeline
    monthly_plan = build_monthly_plan(allocations, recommended, cards_list, profile_dict)

    # Step 5: Compute totals
    total_rewards = sum(float(m.total_expected_value_inr) for m in monthly_plan)

    plan_card_ids = allocated_ids | {r.card_id for r in recommended if r.action == "apply"}

    # Prorate annual fees over the plan timeline to avoid charging a full
    # year of fees for shorter plans.
    timeline_months = float(profile_dict.get("timeline_months", 12) or 12)
    proration_factor = timeline_months / 12.0
    total_fees = sum(
        float(c.get("annual_fee_inr", 0.0) or 0.0) * proration_factor
        for c in cards_list
        if str(c.get("id")) in plan_card_ids
    )

    net_value = total_rewards - total_fees

    if net_value < 0:
        print(
            f"WARNING: net_value_inr is negative (₹{net_value:,.2f}) — fees exceed rewards",
            file=sys.stderr,
        )

    return StrategyPlan(
        session_id=str(profile_dict.get("session_id", "")),
        monthly_plan=monthly_plan,
        recommended_cards=recommended,
        total_rewards_inr=round(float(total_rewards), 2),
        total_fees_inr=round(float(total_fees), 2),
        net_value_inr=round(float(net_value), 2),
    )

