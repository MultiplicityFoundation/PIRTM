from __future__ import annotations

from typing import Iterable, Mapping


def _is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value in (2, 3):
        return True
    if value % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def infinite_prime_check(primes: Iterable[int], min_density: float = 0.05) -> dict:
    """Return a coverage diagnostic for the observed prime indices."""

    primes_list = sorted(set(int(p) for p in primes if _is_prime(int(p))))
    if not primes_list:
        return {"ok": False, "reason": "no primes"}

    largest = primes_list[-1]
    density = len(primes_list) / max(1, largest)
    gaps = [b - a for a, b in zip(primes_list, primes_list[1:])]
    largest_gap = max(gaps) if gaps else 0
    return {
        "ok": density >= min_density,
        "density": density,
        "largest_gap": largest_gap,
        "count": len(primes_list),
        "support": primes_list,
    }
