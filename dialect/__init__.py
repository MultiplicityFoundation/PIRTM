"""
PIRTM Dialect Package

Python implementation of the PIRTM MLIR dialect.

ADR-006: Dialect Type-Layer Gate (Day 0-3)
Spec: PIRTM ADR-004
"""

from pirtm.dialect.pirtm_types import (
    CertType,
    EpsilonType,
    OpNormTType,
    SessionGraphType,
    CouplingType,
    VerificationError,
    create_cert,
    create_epsilon,
    create_op_norm_t,
    create_session_graph,
    is_prime,
    factorize,
)

__all__ = [
    "CertType",
    "EpsilonType",
    "OpNormTType",
    "SessionGraphType",
    "CouplingType",
    "VerificationError",
    "create_cert",
    "create_epsilon",
    "create_op_norm_t",
    "create_session_graph",
    "is_prime",
    "factorize",
]
