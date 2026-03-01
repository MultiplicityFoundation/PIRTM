from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

    from pirtm.conformance import ConformanceResult
    from pirtm.types import Certificate, PETCReport

    from .spec import TranspileSpec


@dataclass(slots=True)
class TranspileResult:
    spec: TranspileSpec
    xi_initial: np.ndarray
    trajectory: list[np.ndarray]
    certificate: Certificate
    petc_report: PETCReport
    audit_export: list[dict]
    lambda_events: list[dict]
    witness_json: dict
    compliance: ConformanceResult
    merkle_root: str
    verdict: str
