from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING, Any

from .types import PETCEntry, PETCReport, StepInfo

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    limit = int(math.sqrt(n)) + 1
    return all(n % k != 0 for k in range(3, limit, 2))


def _prime_count(lo: int, hi: int) -> int:
    if hi < lo:
        return 0
    return sum(1 for value in range(max(2, lo), hi + 1) if _is_prime(value))


def compute_coverage(
    chain: list[int] | tuple[int, ...],
    a: int,
    b: int,
) -> float:
    """Compute PETC coverage ratio ρ(C,[a,b])."""

    lo = int(min(a, b))
    hi = int(max(a, b))
    denominator = _prime_count(lo, hi)
    if denominator == 0:
        return 0.0
    chain_set = {int(value) for value in chain}
    covered = sum(1 for value in range(max(2, lo), hi + 1) if _is_prime(value) and value in chain_set)
    return covered / denominator


def validate_petc_chain(
    chain: list[int] | tuple[int, ...],
    *,
    max_gap: int = 100,
    min_coverage: float = 0.8,
    coverage_window: int = 1000,
) -> dict[str, bool | float | int | list[str]]:
    """Validate PETC chain invariants and report diagnostics."""

    primes = [int(value) for value in chain]
    primality_ok = all(_is_prime(value) for value in primes)
    monotone_ok = all(a < b for a, b in zip(primes, primes[1:], strict=False))
    gaps = [b - a for a, b in zip(primes, primes[1:], strict=False)]
    max_gap_found = max(gaps) if gaps else 0
    gap_ok = max_gap_found <= max_gap

    if primes:
        start = primes[0]
        end = min(primes[-1], start + int(coverage_window))
        coverage = compute_coverage(primes, start, end)
    else:
        coverage = 0.0

    violations: list[str] = []
    if not primality_ok:
        violations.append("Non-prime found in chain")
    if not monotone_ok:
        violations.append("Chain not strictly monotone")
    if not gap_ok:
        violations.append(f"Gap {max_gap_found} exceeds max {max_gap}")
    if coverage < min_coverage:
        violations.append(f"Coverage {coverage:.4f} below minimum {min_coverage:.4f}")

    valid = primality_ok and monotone_ok and gap_ok and coverage >= min_coverage
    return {
        "valid": valid,
        "primality_ok": primality_ok,
        "monotone_ok": monotone_ok,
        "gap_ok": gap_ok,
        "max_gap_found": max_gap_found,
        "coverage": coverage,
        "violations": violations,
    }


class PETCLedger:
    """Append-only prime-indexed event-triggered chain."""

    def __init__(self, *, max_gap: int = 100, min_length: int = 3) -> None:
        self.max_gap = max_gap
        self.min_length = min_length
        self._entries: list[PETCEntry] = []

    def append(
        self,
        prime: int,
        event: Any = None,
        info: StepInfo | None = None,
    ) -> PETCEntry:
        value = int(prime)
        if not _is_prime(value):
            raise ValueError(f"non-prime index: {prime}")
        entry = PETCEntry(prime=value, event=event, info=info, timestamp=time.time())
        self._entries.append(entry)
        return entry

    def entries(self) -> list[PETCEntry]:
        return list(self._entries)

    def __iter__(self) -> Iterator[PETCEntry]:
        return iter(self._entries)

    def __len__(self) -> int:
        return len(self._entries)

    def coverage(self, lo: int, hi: int) -> float:
        values = [entry.prime for entry in self._entries]
        return compute_coverage(values, int(lo), int(hi))

    def validate(self) -> PETCReport:
        primes = [entry.prime for entry in self._entries]
        chain_length = len(primes)
        if chain_length == 0:
            return PETCReport(satisfied=False, chain_length=0)

        violations = [idx for idx, value in enumerate(primes) if not _is_prime(value)]
        monotonic = all(a < b for a, b in zip(primes, primes[1:], strict=False))
        gap_violations = [
            (a, b) for a, b in zip(primes, primes[1:], strict=False) if (b - a) > self.max_gap
        ]
        coverage = self.coverage(primes[0], primes[-1]) if monotonic else 0.0

        satisfied = (
            len(violations) == 0
            and monotonic
            and len(gap_violations) == 0
            and chain_length >= self.min_length
        )
        return PETCReport(
            satisfied=satisfied,
            chain_length=chain_length,
            coverage=coverage,
            gap_violations=gap_violations,
            monotonic=monotonic,
            violations=violations,
            primes_checked=primes,
        )


def petc_invariants(primes: Iterable[int], min_length: int = 3) -> PETCReport:
    """Backward-compatible PETC validation shim."""

    primes_list = [int(value) for value in primes]
    violations = [idx for idx, value in enumerate(primes_list) if not _is_prime(value)]

    if primes_list and len(violations) >= max(1, math.ceil(len(primes_list) / 2)):
        raise ValueError("PETC mass violation: majority of entries are not prime")

    ledger = PETCLedger(min_length=min_length)
    for value in primes_list:
        if _is_prime(value):
            ledger.append(value)
    report = ledger.validate()
    report.violations = violations
    report.primes_checked = primes_list
    report.satisfied = report.satisfied and len(violations) == 0
    return report
