from dataclasses import dataclass
from typing import List, Optional
import heapq


@dataclass(order=True)
class ThresholdEvent:
    month: int
    card_id: str
    required_spend_inr: float
    bonus_value_inr: float


class ThresholdScheduler:
    """
    Priority queue of welcome bonus unlock events.

    This is a minimal placeholder implementation that supports scheduling
    and popping upcoming events but does not implement full strategy logic.
    """

    def __init__(self) -> None:
        self._queue: List[ThresholdEvent] = []

    def add_event(
        self,
        month: int,
        card_id: str,
        required_spend_inr: float,
        bonus_value_inr: float,
    ) -> None:
        heapq.heappush(
            self._queue,
            ThresholdEvent(
                month=month,
                card_id=card_id,
                required_spend_inr=required_spend_inr,
                bonus_value_inr=bonus_value_inr,
            ),
        )

    def next_event(self) -> Optional[ThresholdEvent]:
        if not self._queue:
            return None
        return heapq.heappop(self._queue)

    def has_events(self) -> bool:
        return bool(self._queue)

