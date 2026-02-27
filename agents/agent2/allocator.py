from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from models import CardAllocation
from .reward_matrix import CATEGORIES


def _get_rate_points_per_100(card: Dict[str, Any], category: str) -> float:
    for r in card.get("reward_rates", []) or []:
        if r.get("category") == category:
            return float(r.get("points_per_100", 0.0) or 0.0)
    return 0.0


def make_allocation(
    cards: List[dict],
    card: Dict[str, Any],
    category: str,
    amount_inr: float,
    matrix: np.ndarray,
) -> CardAllocation:
    j = CATEGORIES.index(category)
    card_idx = cards.index(card)
    effective_return = float(matrix[card_idx][j])
    expected_value_inr = float(amount_inr) * effective_return
    points_per_100 = _get_rate_points_per_100(card, category)
    expected_pts = (float(amount_inr) / 100.0) * points_per_100

    return CardAllocation(
        card_id=str(card.get("id")),
        card_name=str(card.get("name", "")),
        category=category,
        amount_inr=round(float(amount_inr), 2),
        expected_pts=round(float(expected_pts), 2),
        expected_value_inr=round(float(expected_value_inr), 2),
    )


def greedy_allocate(
    cards: List[dict],
    profile: Dict[str, Any],
    matrix: np.ndarray,
    cap_matrix: np.ndarray,
    mask: np.ndarray,
) -> List[CardAllocation]:
    """
    Greedily assign the best eligible card to each spending category,
    handling monthly caps with overflow to the next best.
    Returns flat list of CardAllocation for one month.
    """
    masked_matrix = matrix.copy()
    masked_matrix[~mask, :] = -np.inf

    allocations: List[CardAllocation] = []

    for j, category in enumerate(CATEGORIES):
        spend = float((profile.get("spend_breakdown", {}) or {}).get(category, 0.0) or 0.0)
        if spend == 0:
            continue

        col = masked_matrix[:, j]

        if np.all(col == -np.inf):
            continue

        best_idx = int(np.argmax(col))
        best_card = cards[best_idx]
        cap = float(cap_matrix[best_idx][j])

        already_allocated_to_best = sum(
            float(a.amount_inr)
            for a in allocations
            if a.card_id == str(best_card.get("id"))
        )

        if best_card.get("monthly_total_cap_inr", None) is not None:
            remaining_total_cap = float(best_card["monthly_total_cap_inr"]) - already_allocated_to_best
            cap = min(cap, remaining_total_cap)
            if cap <= 0:
                col_copy = col.copy()
                col_copy[best_idx] = -np.inf
                best_idx = int(np.argmax(col_copy))
                best_card = cards[best_idx]
                cap = float(cap_matrix[best_idx][j])

        if cap < spend:
            primary_spend = cap
            overflow_spend = spend - cap

            allocations.append(
                make_allocation(cards, best_card, category, primary_spend, matrix)
            )

            col_copy = col.copy()
            col_copy[best_idx] = -np.inf
            if not np.all(col_copy == -np.inf):
                second_idx = int(np.argmax(col_copy))
                allocations.append(
                    make_allocation(cards, cards[second_idx], category, overflow_spend, matrix)
                )
        else:
            allocations.append(
                make_allocation(cards, best_card, category, spend, matrix)
            )

    return allocations

