from __future__ import annotations

import warnings
from typing import Callable

import numpy as np

from pirtm.gate import EmissionPolicy, GatedOutput
from pirtm.qari import QARIConfig, QARISession
from pirtm.telemetry import MemorySink, TelemetryBus


class DRMMInferenceLoop:
    def __init__(
        self,
        dim: int,
        epsilon: float = 0.05,
        op_norm_T: float = 1.0,
        emission_policy: EmissionPolicy = EmissionPolicy.SUPPRESS,
        convergence_tol: float = 1e-3,
        audit: bool = True,
    ):
        config = QARIConfig(
            dim=dim,
            epsilon=epsilon,
            op_norm_T=op_norm_T,
            emission_policy=emission_policy,
            adaptive=True,
            audit=audit,
            convergence_tol=convergence_tol,
        )
        self._sink = MemorySink()
        self._bus = TelemetryBus(sinks=[self._sink])
        self._session = QARISession(config, telemetry=self._bus)

    def evolve(
        self,
        X: np.ndarray,
        Xi: np.ndarray,
        Lam: np.ndarray,
        T: Callable[[np.ndarray], np.ndarray],
        G: np.ndarray | None = None,
    ) -> tuple[np.ndarray, GatedOutput]:
        if G is None:
            G = np.zeros_like(X)
        result = self._session.step(X, Xi, Lam, T, G)
        return result.X_next, result

    def run(
        self,
        X0: np.ndarray,
        Xi_seq: list[np.ndarray],
        Lam_seq: list[np.ndarray],
        T: Callable[[np.ndarray], np.ndarray],
        G_seq: list[np.ndarray] | None = None,
    ) -> dict:
        n_steps = len(Xi_seq)
        if G_seq is None:
            G_seq = [np.zeros_like(X0)] * n_steps

        X = np.array(X0, copy=True)
        history = [np.array(X, copy=True)]
        outputs: list[GatedOutput] = []

        for Xi_t, Lam_t, G_t in zip(Xi_seq, Lam_seq, G_seq):
            X, out = self.evolve(X, Xi_t, Lam_t, T, G_t)
            history.append(np.array(X, copy=True))
            outputs.append(out)

        cert = self._session.certify()
        return {
            "X_final": X,
            "history": history,
            "outputs": outputs,
            "certificate": cert,
            "summary": self._session.summary(),
            "audit_export": self._session.audit_chain.export() if self._session.audit_chain else None,
        }

    @property
    def session(self) -> QARISession:
        return self._session

    @property
    def telemetry_events(self):
        return self._sink.events


class EntropicFeedbackLoop:
    def __init__(self, alpha: float = 0.1):
        warnings.warn(
            "EntropicFeedbackLoop is deprecated. Use DRMMInferenceLoop.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.alpha = alpha

    def entropy_gradient(self, X):
        return -np.log(np.abs(X) + 1e-8)

    def update(self, X, t):
        return X + self.alpha * t * self.entropy_gradient(X)


class ConvergenceController:
    def __init__(self, threshold: float = 1e-3):
        warnings.warn(
            "ConvergenceController is deprecated. Use pirtm.recurrence.run().",
            DeprecationWarning,
            stacklevel=2,
        )
        self.threshold = threshold

    def is_converged(self, X_old, X_new):
        return np.linalg.norm(X_new - X_old) < self.threshold


class EthicalModulator:
    def __init__(self, filter_strength: float = 0.05):
        warnings.warn(
            "EthicalModulator is deprecated. Use pirtm.gate.EmissionGate.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.f = lambda x: np.tanh(x)
        self.lam = filter_strength

    def apply(self, X):
        return X - self.lam * self.f(X)
