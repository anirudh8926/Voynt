from typing import Dict, List, Tuple

import numpy as np


def build_reward_matrix(cards: List[dict]) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Build a simple cards × categories → effective INR return matrix.

    This is a placeholder implementation that infers categories from the
    `reward_rates` child relation if present. If no reward data is available,
    it returns an empty matrix.
    """
    categories_set = set()
    for card in cards:
        for rr in card.get("reward_rates", []) or []:
            cat = rr.get("category")
            if cat:
                categories_set.add(cat)

    if not categories_set:
        return np.zeros((0, 0)), [], []

    categories = sorted(categories_set)
    card_ids = [str(card.get("id")) for card in cards]

    matrix = np.zeros((len(card_ids), len(categories)))
    card_index: Dict[str, int] = {cid: idx for idx, cid in enumerate(card_ids)}
    category_index: Dict[str, int] = {cat: idx for idx, cat in enumerate(categories)}

    for card in cards:
        cid = str(card.get("id"))
        i = card_index.get(cid)
        if i is None:
            continue
        for rr in card.get("reward_rates", []) or []:
            cat = rr.get("category")
            j = category_index.get(cat)
            if j is None:
                continue
            points_per_100 = float(rr.get("points_per_100", 0.0))
            point_value_inr = float(card.get("point_value_inr", 0.0))
            effective_return = (points_per_100 * point_value_inr) / 100.0
            matrix[i, j] = effective_return

    return matrix, card_ids, categories

