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

__version__ = "0.1.0dev0"

from .types import (
    StepInfo,
    Status,
    Certificate,
    PETCReport,
    PETCEntry,
    MonitorRecord,
    WeightSchedule,
    CSCBudget,
    CSCMargin,
)
from .recurrence import step, run
from .projection import (
    project_parameters_soft,
    project_parameters_weighted_l1,
)
from .certify import ace_certificate, ace_certificate_v2, iss_bound, legacy_ace_certificate
from .fixed_point import fixed_point_estimate
from .adaptive import AdaptiveMargin
from .petc import PETCLedger, petc_invariants
from .infinite_prime import infinite_prime_check
from .monitor import Monitor
from .weights import synthesize_weights, validate_schedule
from .gain import estimate_operator_norm, build_gain_sequence, check_iss_compatibility
from .csc import solve_budget, compute_margin, multi_step_margin, sensitivity
from .integrations import drmm_step, drmm_evolve
from .gate import EmissionGate, EmissionPolicy, GatedOutput, gated_run
from .telemetry import (
    TelemetryEvent,
    TelemetrySink,
    NullSink,
    MemorySink,
    FileSink,
    CallbackSink,
    AlertRule,
    TelemetryBus,
    projection_rate_alert,
    q_divergence_alert,
)
from .audit import AuditEvent, AuditChain
from .qari import QARIConfig, QARISession
from .integrations import DRMMInferenceLoop
from .csl import (
    CSLVerdict,
    SilenceEvent,
    neutrality_check,
    beneficence_check,
    silence_clause,
    commutation_check,
    evaluate_csl,
)
from .csl_gate import CSLGatedOutput, CSLEmissionGate
from .spectral_decomp import spectral_decomposition, spectral_entropy, phase_coherence, analyze_tensor
from .spectral_gov import SpectralReport, SpectralGovernor
from .orchestrator import SessionDescriptor, AggregatedCertificate, SessionSnapshot, SessionOrchestrator
from .lambda_bridge import LambdaTraceEvent, SubmissionReceipt, LambdaTraceBridge
from .petc_bridge import PETCAllocation, PETCAllocator
from .transpiler import TranspileResult, TranspileSpec, transpile
from .ace import (
    AceBudget,
    AceBudgetState,
    AceCertificate,
    AceProtocol,
    AceTelemetry,
    AceWitness,
    CertLevel,
)

__all__ = [
    "StepInfo",
    "Status",
    "Certificate",
    "PETCReport",
    "PETCEntry",
    "MonitorRecord",
    "WeightSchedule",
    "CSCBudget",
    "CSCMargin",
    # core
    "step",
    "run",
    # projection
    "project_parameters_soft",
    "project_parameters_weighted_l1",
    # certificates / bounds
    "ace_certificate",
    "ace_certificate_v2",
    "legacy_ace_certificate",
    "iss_bound",
    # fixed point
    "fixed_point_estimate",
    # adaptive
    "AdaptiveMargin",
    # PETC
    "PETCLedger",
    "petc_invariants",
    # monitors
    "Monitor",
    # prime coverage
    "infinite_prime_check",
    # weights
    "synthesize_weights",
    "validate_schedule",
    # gain
    "estimate_operator_norm",
    "build_gain_sequence",
    "check_iss_compatibility",
    # CSC
    "solve_budget",
    "compute_margin",
    "multi_step_margin",
    "sensitivity",
    # gate
    "EmissionGate",
    "EmissionPolicy",
    "GatedOutput",
    "gated_run",
    # telemetry
    "TelemetryEvent",
    "TelemetrySink",
    "NullSink",
    "MemorySink",
    "FileSink",
    "CallbackSink",
    "AlertRule",
    "TelemetryBus",
    "projection_rate_alert",
    "q_divergence_alert",
    # audit
    "AuditEvent",
    "AuditChain",
    # csl
    "CSLVerdict",
    "SilenceEvent",
    "neutrality_check",
    "beneficence_check",
    "silence_clause",
    "commutation_check",
    "evaluate_csl",
    "CSLGatedOutput",
    "CSLEmissionGate",
    # spectral
    "spectral_decomposition",
    "spectral_entropy",
    "phase_coherence",
    "analyze_tensor",
    "SpectralReport",
    "SpectralGovernor",
    # orchestrator
    "SessionDescriptor",
    "AggregatedCertificate",
    "SessionSnapshot",
    "SessionOrchestrator",
    # lambda bridge
    "LambdaTraceEvent",
    "SubmissionReceipt",
    "LambdaTraceBridge",
    # petc bridge
    "PETCAllocation",
    "PETCAllocator",
    # qari
    "QARIConfig",
    "QARISession",
    # integrations
    "drmm_step",
    "drmm_evolve",
    "DRMMInferenceLoop",
    # ACE protocol
    "AceBudget",
    "AceBudgetState",
    "AceCertificate",
    "AceProtocol",
    "AceTelemetry",
    "AceWitness",
    "CertLevel",
    # transpiler
    "TranspileSpec",
    "TranspileResult",
    "transpile",
]
