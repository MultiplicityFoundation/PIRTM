from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Any, Callable

import numpy as np

from .certify import ace_certificate
from .recurrence import run
from .types import StepInfo


@dataclass
class ConformanceResult:
    profile: str
    pirtm_version: str = "0.1.0dev0"
    checks: list[dict[str, Any]] | None = None
    passed: bool = True

    def __post_init__(self) -> None:
        if self.checks is None:
            self.checks = []

    def record(self, name: str, passed: bool, detail: str = "") -> None:
        self.checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            self.passed = False

    def to_json(self) -> str:
        return json.dumps(
            {
                "profile": self.profile,
                "pirtm_version": self.pirtm_version,
                "passed": self.passed,
                "checks": self.checks,
            },
            indent=2,
        )


def check_core_profile(
    X0: np.ndarray,
    Xi_seq: list[np.ndarray],
    Lam_seq: list[np.ndarray],
    G_seq: list[np.ndarray],
    T: Callable[[np.ndarray], np.ndarray],
    P: Callable[[np.ndarray], np.ndarray],
    *,
    epsilon: float = 0.05,
    op_norm_T: float = 1.0,
) -> ConformanceResult:
    result = ConformanceResult(profile="core")
    _, _, infos, _ = run(
        X0,
        Xi_seq,
        Lam_seq,
        G_seq,
        T=T,
        P=P,
        epsilon=epsilon,
        op_norm_T=op_norm_T,
    )

    result.record(
        "predicate_evaluation",
        all(info.q is not None for info in infos),
        f"q computed for {len(infos)} steps",
    )

    unmitigated = [info for info in infos if info.q > 1 - epsilon and not info.projected]
    result.record("fail_closed", len(unmitigated) == 0, f"unmitigated={len(unmitigated)}")

    _, _, infos2, _ = run(
        X0,
        Xi_seq,
        Lam_seq,
        G_seq,
        T=T,
        P=P,
        epsilon=epsilon,
        op_norm_T=op_norm_T,
    )
    deterministic = len(infos) == len(infos2) and all(
        abs(a.q - b.q) < 1e-12 and a.projected == b.projected for a, b in zip(infos, infos2)
    )
    result.record("deterministic_remediation", deterministic, "repeat run equality")

    try:
        for info in infos:
            json.dumps(asdict(info))
        serializable = True
    except Exception:
        serializable = False
    result.record("canonical_fingerprint", serializable, "StepInfo json serialization")

    cert = ace_certificate(infos)
    result.record(
        "certificate_consistency",
        cert.certified == (cert.margin >= 0),
        f"margin={cert.margin:.6f}",
    )
    return result


def check_integrity_profile(infos: list[StepInfo]) -> ConformanceResult:
    result = ConformanceResult(profile="integrity")
    steps = [info.step for info in infos]
    result.record("canonical_ordering", steps == sorted(steps), f"n={len(steps)}")
    result.record("anti_replay", len(steps) == len(set(steps)), f"unique={len(set(steps))}")

    trace_a = [json.dumps(asdict(info), sort_keys=True) for info in infos]
    trace_b = [json.dumps(asdict(info), sort_keys=True) for info in infos]
    result.record("deterministic_trace", trace_a == trace_b, "sorted-key deterministic encoding")
    return result


def _cli_main() -> None:
    parser = argparse.ArgumentParser(description="PIRTM conformance checker")
    parser.add_argument("--profile", choices=["core", "integrity", "all"], default="all")
    parser.add_argument("--dim", type=int, default=4)
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--epsilon", type=float, default=0.05)
    parser.add_argument("--output", choices=["text", "json"], default="text")
    args = parser.parse_args()

    dim = args.dim
    n_steps = args.steps
    X0 = np.ones(dim)
    Xi_seq = [0.3 * np.eye(dim)] * n_steps
    Lam_seq = [0.2 * np.eye(dim)] * n_steps
    G_seq = [np.zeros(dim)] * n_steps
    T = lambda x: 0.8 * x
    P = lambda x: x

    results: list[ConformanceResult] = []
    if args.profile in ("core", "all"):
        results.append(
            check_core_profile(X0, Xi_seq, Lam_seq, G_seq, T, P, epsilon=args.epsilon, op_norm_T=0.8)
        )

    if args.profile in ("integrity", "all"):
        _, _, infos, _ = run(
            X0,
            Xi_seq,
            Lam_seq,
            G_seq,
            T=T,
            P=P,
            epsilon=args.epsilon,
            op_norm_T=0.8,
        )
        results.append(check_integrity_profile(infos))

    exit_code = 0
    for item in results:
        if args.output == "json":
            print(item.to_json())
        else:
            mark = "PASS" if item.passed else "FAIL"
            print(f"[{mark}] profile={item.profile}")
            for check in item.checks:
                cmark = "+" if check["passed"] else "X"
                print(f"  [{cmark}] {check['name']}: {check['detail']}")
        if not item.passed:
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    _cli_main()
