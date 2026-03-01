from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .petc import _is_prime, petc_invariants

if TYPE_CHECKING:
    from .audit import AuditChain
    from .types import PETCReport


def _prime_stream(count: int) -> list[int]:
    primes: list[int] = []
    value = 2
    while len(primes) < count:
        if _is_prime(value):
            primes.append(value)
        value += 1
    return primes


@dataclass(frozen=True)
class PETCAllocation:
    session_id: str
    prime_base: int
    prime_stride: int
    allocated_primes: list[int]
    report: PETCReport


class PETCAllocator:
    def __init__(self, max_sessions: int = 100):
        self.max_sessions = max_sessions
        self._allocations: dict[str, PETCAllocation] = {}
        self._session_order: dict[str, int] = {}

    def allocate(self, session_id: str, event_count: int) -> PETCAllocation:
        if session_id in self._allocations:
            return self._allocations[session_id]

        if len(self._session_order) >= self.max_sessions:
            raise ValueError("maximum number of sessions exceeded")

        if event_count < 0:
            raise ValueError("event_count must be non-negative")

        offset = len(self._session_order)
        self._session_order[session_id] = offset

        required = offset + (event_count * self.max_sessions)
        primes_pool = _prime_stream(max(required, event_count + offset + 1))
        allocated = primes_pool[
            offset : offset + event_count * self.max_sessions : self.max_sessions
        ]

        report = petc_invariants(allocated, min_length=min(3, event_count))
        allocation = PETCAllocation(
            session_id=session_id,
            prime_base=allocated[0] if allocated else 2,
            prime_stride=self.max_sessions,
            allocated_primes=allocated,
            report=report,
        )
        self._allocations[session_id] = allocation
        return allocation

    def tag_audit_chain(self, session_id: str, chain: AuditChain) -> list[tuple[int, str]]:
        allocation = self.allocate(session_id, len(chain))
        return [
            (prime, event.chain_hash)
            for event, prime in zip(chain, allocation.allocated_primes, strict=False)
        ]

    def verify_global_ordering(self) -> dict[str, Any]:
        all_primes: list[int] = []
        for allocation in self._allocations.values():
            all_primes.extend(allocation.allocated_primes)

        unique = set(all_primes)
        collisions = len(all_primes) - len(unique)
        return {
            "total_primes": len(all_primes),
            "unique_primes": len(unique),
            "collisions": collisions,
            "globally_ordered": collisions == 0,
            "sessions": len(self._allocations),
        }

    @property
    def allocations(self) -> dict[str, PETCAllocation]:
        return dict(self._allocations)
