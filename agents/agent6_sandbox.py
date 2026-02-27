from typing import Dict, List, Optional

from models import SandboxRequest, SandboxResponse, StrategyPlan


def run_agent6(
    request: SandboxRequest,
    cards: List[dict],
    ai_strategy: Optional[StrategyPlan],
) -> SandboxResponse:
    """
    Lightweight reward recalculation for sandbox mode.

    Placeholder implementation:
    - Treats all rewards as a flat 1% cashback on spend_overrides.
    - Computes diff_vs_ai_inr relative to ai_strategy.total_rewards_inr, if provided.
    - Does NOT run full Monte Carlo; simulation_result is always None.
    """
    # Flatten spend_overrides into total spend
    total_spend = 0.0
    for card_id, cat_map in request.spend_overrides.items():
        for _category, amount in cat_map.items():
            total_spend += float(amount)

    # Simple 1% cashback approximation
    computed_rewards_inr = total_spend * 0.01

    # Basic yield index as rewards / spend (guard against zero)
    if total_spend > 0:
        yield_index = computed_rewards_inr / total_spend
    else:
        yield_index = 0.0

    ai_total = ai_strategy.total_rewards_inr if ai_strategy is not None else 0.0
    diff_vs_ai_inr = computed_rewards_inr - ai_total

    return SandboxResponse(
        computed_rewards_inr=computed_rewards_inr,
        yield_index=yield_index,
        diff_vs_ai_inr=diff_vs_ai_inr,
        simulation_result=None,
    )

