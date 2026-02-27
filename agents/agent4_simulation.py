from typing import Dict

import numpy as np

from models import SimulationResult, StrategyPlan, UserProfile


RISK_SIGMA: Dict[str, float] = {
    "low": 0.10,
    "medium": 0.20,
    "high": 0.35,
}


async def run_agent4(strategy: StrategyPlan, profile: UserProfile) -> SimulationResult:
    """
    Monte Carlo simulation. 10,000 trials using NumPy vectorization.

    Placeholder implementation that treats the strategy's net value as the
    mean outcome and scales volatility by the user's risk level. It still
    follows the requested data contract and returns a full SimulationResult.
    """
    trials = 10_000

    base_value = float(strategy.net_value_inr or strategy.total_rewards_inr or 0.0)
    sigma_factor = RISK_SIGMA.get(profile.risk_level, RISK_SIGMA["medium"])
    sigma = max(abs(base_value) * sigma_factor, 1.0)

    outcomes = np.random.normal(loc=base_value, scale=sigma, size=trials)

    goal_amount = float(profile.goal_amount_inr or 0.0)
    success_probability = float(np.mean(outcomes >= goal_amount)) if trials > 0 else 0.0

    p10 = float(np.percentile(outcomes, 10))
    p50 = float(np.percentile(outcomes, 50))
    p90 = float(np.percentile(outcomes, 90))
    worst = float(np.min(outcomes))
    best = float(np.max(outcomes))

    if best == worst:
        buckets = [worst]
        counts = [trials]
    else:
        counts, edges = np.histogram(outcomes, bins=20, range=(worst, best))
        buckets = [(float(edges[i]) + float(edges[i + 1])) / 2.0 for i in range(len(edges) - 1)]

    histogram_data = [
        {"bucket_inr": float(bucket), "count": int(count)}
        for bucket, count in zip(buckets, counts)
    ]

    risk_score = float((1.0 - success_probability) * 100.0)

    return SimulationResult(
        session_id=strategy.session_id,
        success_probability=success_probability,
        p10_inr=p10,
        p50_inr=p50,
        p90_inr=p90,
        worst_case_inr=worst,
        best_case_inr=best,
        risk_score=risk_score,
        histogram_data=histogram_data,
        run_count=trials,
    )

