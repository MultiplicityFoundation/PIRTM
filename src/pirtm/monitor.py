from __future__ import annotations

from collections import deque
from typing import Deque, Iterable, Optional

from .types import MonitorRecord, Status, StepInfo


class Monitor:
    """Lightweight rolling monitor for PIRTM telemetry."""

    def __init__(self, maxlen: int = 512):
        self.records: Deque[MonitorRecord] = deque(maxlen=maxlen)

    def push(self, info: StepInfo, status: Optional[Status] = None) -> MonitorRecord:
        record = MonitorRecord(step=info.step, info=info, status=status)
        self.records.append(record)
        return record

    def summary(self) -> dict:
        if not self.records:
            return {"steps": 0, "max_q": 0.0, "converged": False}
        steps = len(self.records)
        max_q = max(r.info.q for r in self.records)
        converged = bool(self.records[-1].status and self.records[-1].status.converged)
        return {"steps": steps, "max_q": max_q, "converged": converged}

    def __iter__(self):
        return iter(self.records)

    def last(self) -> Optional[MonitorRecord]:
        return self.records[-1] if self.records else None
