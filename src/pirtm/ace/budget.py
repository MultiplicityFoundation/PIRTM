from __future__ import annotations

from .types import AceBudgetState

class AceBudget:
    """Tracks ACE budget consumption across certification calls."""

    def __init__(self, tau: float = 1.0) -> None:
        if tau <= 0:
            raise ValueError("tau must be > 0")
        self._tau = float(tau)
        self._consumed = 0.0
        self._depletion_rate = 0.0

    def consume(self, amount: float) -> AceBudgetState:
        if amount < 0:
            raise ValueError("budget consumption must be >= 0")
        self._consumed += float(amount)
        self._depletion_rate = float(amount)
        if self._consumed >= self._tau:
            raise RuntimeError(
                f"ACE_BUDGET_DEPLETED: consumed={self._consumed:.4f} >= tau={self._tau:.4f}"
            )
        return self.snapshot()

    def snapshot(self) -> AceBudgetState:
        return AceBudgetState(
            tau=self._tau,
            consumed=self._consumed,
            depletion_rate=self._depletion_rate,
        )
