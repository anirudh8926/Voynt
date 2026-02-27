import asyncio
from typing import Dict, List

from db import supabase, update_session_status
from models import SimulationResult, StrategyPlan, UserProfile, YieldResult
from agents.agent2 import run_agent2
from agents.agent3_yield import run_agent3
from agents.agent4_simulation import run_agent4
from agents.agent5_narrative import run_agent5


async def run_pipeline(profile: UserProfile, cards: List[Dict]) -> Dict:
    session_id = profile.session_id

    try:
        # Stage 1: Strategy (Agent 2) — synchronous, fast
        update_session_status(session_id, "processing")
        strategy: StrategyPlan = run_agent2(profile, cards)

        # Stage 2: Yield Index (Agent 3) — synchronous, instant
        yield_result: YieldResult = run_agent3(strategy, profile)

        # Write strategy + yield to DB immediately
        # Frontend can render the plan table while simulation runs
        supabase.table("strategy_results").insert(
            {
                "session_id": session_id,
                "monthly_plan": [m.model_dump() for m in strategy.monthly_plan],
                "recommended_cards": [
                    c.model_dump() for c in strategy.recommended_cards
                ],
                "total_rewards_inr": strategy.total_rewards_inr,
                "total_fees_inr": strategy.total_fees_inr,
                "net_value_inr": strategy.net_value_inr,
                "yield_index": yield_result.yield_index,
                "break_even_month": yield_result.break_even_month,
            }
        ).execute()

        # Stage 3+4: Simulation + Narrative — run concurrently (both are slow)
        simulation, narrative = await asyncio.gather(
            run_agent4(strategy, profile),
            run_agent5(strategy, yield_result, profile),
        )

        # Write simulation result — Supabase Realtime fires here, updating frontend gauge
        supabase.table("simulation_results").insert(
            {
                "session_id": session_id,
                "success_probability": simulation.success_probability,
                "p10_inr": simulation.p10_inr,
                "p50_inr": simulation.p50_inr,
                "p90_inr": simulation.p90_inr,
                "worst_case_inr": simulation.worst_case_inr,
                "best_case_inr": simulation.best_case_inr,
                "risk_score": simulation.risk_score,
                "histogram_data": simulation.histogram_data,
                "run_count": simulation.run_count,
            }
        ).execute()

        # Write narrative to strategy_results
        supabase.table("strategy_results").update(
            {"ai_narrative": narrative}
        ).eq("session_id", session_id).execute()

        update_session_status(session_id, "complete")

        return {
            "strategy": strategy,
            "simulation": simulation,
            "yield_result": yield_result,
            "ai_narrative": narrative,
        }

    except Exception as e:  # pragma: no cover - defensive path
        update_session_status(session_id, "failed")
        raise e

