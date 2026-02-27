"""PIRTM – Prime-Indexed Recursive Tensor Mathematics

This package provides the *drop-in* components that Q-ARI's core loop calls:
- Contractive recurrence step with soft projection
- Weighted-\u21111 projector for parameter budgets
- ACE (numeric) + PETC (prime-typed) certificates
- Fixed-point estimator with certified tail bound
- Adaptive margin controller
- Infinite-prime convergence/coverage checks
- Lightweight monitoring & safety status

Typical one-step usage
----------------------
>>> from pirtm.recurrence import step
>>> from pirtm.certify import ace_certificate
>>> x1, info = step(x0, Xi_t, Lam_t, T, g_t, P, epsilon=0.05, op_norm_T=1.0)
>>> cert = ace_certificate(info)
>>> assert cert.certified

The modules are dependency-light (NumPy only) and pure-Python.
"""

from .types import StepInfo, Status, Certificate, PETCReport, MonitorRecord
from .recurrence import step, run
from .projection import (
    project_parameters_soft,
    project_parameters_weighted_l1,
)
from .certify import ace_certificate, iss_bound
from .fixed_point import fixed_point_estimate
from .adaptive import AdaptiveMargin
from .petc import petc_invariants
from .infinite_prime import infinite_prime_check
from .monitor import Monitor

__all__ = [
    "StepInfo",
    "Status",
    "Certificate",
    "PETCReport",
    "MonitorRecord",
    # core
    "step",
    "run",
    # projection
    "project_parameters_soft",
    "project_parameters_weighted_l1",
    # certificates / bounds
    "ace_certificate",
    "iss_bound",
    # fixed point
    "fixed_point_estimate",
    # adaptive
    "AdaptiveMargin",
    # PETC
    "petc_invariants",
    # monitors
    "Monitor",
    # prime coverage
    "infinite_prime_check",
]
