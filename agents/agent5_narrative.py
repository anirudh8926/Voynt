import os
from typing import Optional

from anthropic import Anthropic, APIError

from models import StrategyPlan, UserProfile, YieldResult


def _build_prompt(
    strategy: StrategyPlan,
    yield_result: YieldResult,
    profile: UserProfile,
) -> str:
    return (
        "You are an expert credit card reward strategist.\n"
        "The user is in India and wants to optimize credit card rewards.\n\n"
        f"User goal: {profile.goal_text} (₹{profile.goal_amount_inr} in "
        f"{profile.timeline_months} months)\n"
        f"Risk level: {profile.risk_level}\n"
        f"Yield index: {yield_result.yield_index:.4f}\n"
        f"Net value (INR): {yield_result.net_value_inr:.2f}\n\n"
        "Spend breakdown (monthly, INR):\n"
        + "\n".join(
            f"- {k}: ₹{v:.0f}" for k, v in profile.spend_breakdown.items()
        )
        + "\n\n"
        "Strategy overview:\n"
        f"- Total rewards: ₹{strategy.total_rewards_inr:.2f}\n"
        f"- Total fees: ₹{strategy.total_fees_inr:.2f}\n"
        f"- Net value: ₹{strategy.net_value_inr:.2f}\n"
        "\n"
        "Based on this, write exactly 3 bullet points:\n"
        "1. The single highest-impact action the user should take.\n"
        "2. The biggest risk in the plan and how to mitigate it.\n"
        "3. What success looks like if the plan is followed.\n"
        "Do not add any extra text before or after the bullets.\n"
    )


async def run_agent5(
    strategy: StrategyPlan,
    yield_result: YieldResult,
    profile: UserProfile,
) -> str:
    """
    Call Claude API (claude-sonnet-4-6) to generate plain-language strategy explanation.
    Returns a narrative as a plain string. If the API is unavailable, returns a
    fallback narrative with the correct bullet structure.
    """
    api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    prompt = _build_prompt(strategy, yield_result, profile)

    if not api_key:
        return (
            "- Focus your highest monthly spend category on the card with the best reward rate to accelerate earning towards your goal.\n"
            "- The biggest risk is overspending or missing due dates; mitigate this by setting up autopay and tracking monthly spend against your budget.\n"
            "- If you follow this plan consistently, you should reach your target rewards balance in line with the suggested timeline."
        )

    client = Anthropic(api_key=api_key)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            system=(
                "You are a concise financial coach for Indian credit card users. "
                "Always respond with exactly three bullet points, no introductions or conclusions."
            ),
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        # messages.create returns a Message object whose 'content' is a list
        # of content blocks. For simple text responses, we join all text parts.
        parts = []
        for block in message.content:
            if hasattr(block, "text"):
                parts.append(block.text)
            elif isinstance(block, dict) and "text" in block:
                parts.append(str(block["text"]))
        narrative = "\n".join(parts).strip()
        if not narrative:
            raise ValueError("Empty narrative from Claude")
        return narrative

    except (APIError, Exception):
        return (
            "- Use your strongest rewards card for everyday spend and time major purchases to align with welcome bonus thresholds.\n"
            "- The main risk is variability in your monthly spending; reduce it by keeping a fixed baseline budget and avoiding unnecessary new EMIs.\n"
            "- Hitting the planned spend and paying on time should leave you with enough rewards to cover most or all of your goal by the target date."
        )

