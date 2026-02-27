from models import StrategyPlan, UserProfile, YieldResult


def run_agent3(strategy: StrategyPlan, profile: UserProfile) -> YieldResult:
    """
    Compute yield index.
    Formula: (total_rewards - fees - opportunity_cost) / total_spend
    Opportunity cost = total_spend x (0.07 / 12) x timeline_months  (7% p.a. FD rate)
    Efficiency score: benchmark yield_index against a flat 1% cashback baseline
    """
    total_spend = profile.monthly_spend_inr * profile.timeline_months
    if total_spend <= 0:
        return YieldResult(
            session_id=strategy.session_id,
            yield_index=0.0,
            break_even_month=profile.timeline_months,
            total_rewards_inr=strategy.total_rewards_inr,
            total_fees_inr=strategy.total_fees_inr,
            net_value_inr=strategy.net_value_inr,
            efficiency_score=0.0,
        )

    opportunity_cost = total_spend * (0.07 / 12) * profile.timeline_months
    numerator = strategy.total_rewards_inr - strategy.total_fees_inr - opportunity_cost
    yield_index = numerator / total_spend

    baseline_yield = 0.01
    efficiency_score = max(0.0, (yield_index / baseline_yield) * 50) if baseline_yield > 0 else 0.0
    efficiency_score = min(efficiency_score, 100.0)

    break_even_month = profile.timeline_months

    return YieldResult(
        session_id=strategy.session_id,
        yield_index=yield_index,
        break_even_month=break_even_month,
        total_rewards_inr=strategy.total_rewards_inr,
        total_fees_inr=strategy.total_fees_inr,
        net_value_inr=strategy.net_value_inr,
        efficiency_score=efficiency_score,
    )

