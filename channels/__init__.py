"""PIRTM Channel compatibility shim for prime → mod migration.

This module provides backward-compatible interfaces during the Day 0–14 migration
from `.prime` nomenclature to `.mod` canonical form.

Spec Reference: PIRTM ADR-004, ADR-007
"""

from .shim import PrimeChannelShim, SessionGraphShim

__all__ = ["PrimeChannelShim", "SessionGraphShim"]
