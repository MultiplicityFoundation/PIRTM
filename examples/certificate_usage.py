"""End-to-end examples for PIRTM certificate APIs."""

from __future__ import annotations

import numpy as np

from pirtm import ace_certificate, contraction_certificate, iss_bound, run, step


def _t_fn(value: np.ndarray) -> np.ndarray:
    return 0.8 * value


def _p_fn(value: np.ndarray) -> np.ndarray:
    return value


def simple_validation() -> None:
    """Basic contraction validation using the primary certificate API."""
    x = np.ones(4)
    xi = 0.3 * np.eye(4)
    lam = 0.2 * np.eye(4)
    g = np.zeros(4)

    _, info = step(x, xi, lam, _t_fn, g, _p_fn, epsilon=0.05, op_norm_T=0.8)
    cert = contraction_certificate(info)

    print("Simple validation")
    print(f"  certified={cert.certified}")
    print(f"  margin={cert.margin:.6f}")
    print(f"  tail_bound={cert.tail_bound:.6f}")


def advanced_diagnostics() -> None:
    """Aggregate ACE diagnostics over a short run."""
    x0 = np.ones(4)
    n_steps = 10
    xi_seq = [0.3 * np.eye(4)] * n_steps
    lam_seq = [0.2 * np.eye(4)] * n_steps
    g_seq = [np.zeros(4)] * n_steps

    _, _, infos, _ = run(
        x0,
        xi_seq,
        lam_seq,
        g_seq,
        T=_t_fn,
        P=_p_fn,
        epsilon=0.05,
        op_norm_T=0.8,
    )
    ace = ace_certificate(infos)

    print("Advanced ACE diagnostics")
    print(f"  certified={ace.certified}")
    print(f"  margin={ace.margin:.6f}")
    print(f"  tail_bound={ace.tail_bound:.6f}")
    print(f"  max_q={ace.details.get('max_q'):.6f}")
    print(f"  target={ace.details.get('target'):.6f}")


def iss_stability() -> None:
    """Compute the ISS bound from one-step telemetry."""
    x = np.ones(4)
    xi = 0.3 * np.eye(4)
    lam = 0.2 * np.eye(4)
    g = 0.1 * np.ones(4)

    _, info = step(x, xi, lam, _t_fn, g, _p_fn, epsilon=0.05, op_norm_T=0.8)
    disturbance_norm = float(np.linalg.norm(g, ord=np.inf))
    bound = iss_bound(info, disturbance_norm)

    print("ISS bound")
    print(f"  disturbance_norm={disturbance_norm:.6f}")
    print(f"  bound={bound:.6f}")


if __name__ == "__main__":
    simple_validation()
    advanced_diagnostics()
    iss_stability()
