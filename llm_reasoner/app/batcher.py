from typing import List
from datetime import timedelta
from .schemas import Event

def build_batch(events: List[Event], window_sec=10) -> List[Event]:
    if len(events) == 0:
        return []

    events_sorted = sorted(events, key=lambda e: e.timestamp)
    latest = events_sorted[-1].timestamp
    window_start = latest - timedelta(seconds=window_sec)

    batch = [e for e in events_sorted if e.timestamp >= window_start]
    return batch[-40:]   # 최대 40개까지만 자르기 (token 관리)

