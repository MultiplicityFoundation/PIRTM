"""
AAA (Adaptive Antoulas-Anderson) rational approximation.
Nakatsukasa, Sète, Trefethen (2018). SIAM J. Sci. Comput.

@spec: ADR-017 (Track B — pole detection via rational approximant)
Self-contained: no external rational-approx dependency required.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass


@dataclass
class AAAResult:
    """
    Output of the AAA algorithm.
    r(z) = numerator(z) / denominator(z) in barycentric form.
    poles: complex array of poles of the rational approximant.
    residuals: residues at each pole.
    err: sup-norm of approximation error on sample set.
    support_indices: indices of chosen support points in Z.
    """
    poles: np.ndarray
    residuals: np.ndarray
    weights: np.ndarray
    nodes: np.ndarray
    values: np.ndarray
    err: float
    support_indices: list[int]

    def __call__(self, z: complex | np.ndarray) -> np.ndarray:
        """Evaluate rational approximant at z (scalar or array)."""
        z = np.asarray(z, dtype=complex)
        scalar = z.ndim == 0
        z = np.atleast_1d(z)
        out = np.empty_like(z)
        for i, zi in enumerate(z):
            diffs = zi - self.nodes
            if np.any(diffs == 0):
                # Evaluate exactly at a node
                idx = np.where(diffs == 0)[0][0]
                out[i] = self.values[idx]
            else:
                C = 1.0 / diffs
                out[i] = (C @ (self.weights * self.values)) / (C @ self.weights)
        return out[0] if scalar else out


def aaa(
    Z: np.ndarray,
    F: np.ndarray,
    tol: float = 1e-13,
    mmax: int = 100,
) -> AAAResult:
    """
    AAA algorithm: rational approximant to f sampled at Z.

    Parameters
    ----------
    Z : complex array, shape (M,) — sample points
    F : complex array, shape (M,) — function values f(Z)
    tol : float — relative tolerance for convergence
    mmax : int — maximum number of support points

    Returns
    -------
    AAAResult with poles, residuals, barycentric weights, error.

    @spec: ADR-017 Track B
    """
    z_full = np.asarray(Z, dtype=complex).ravel()
    f_full = np.asarray(F, dtype=complex).ravel()
    M = len(Z)

    # Scale factor
    sf = np.max(np.abs(F))
    if sf == 0:
        sf = 1.0

    # Initialize
    J = list(range(M))          # indices NOT yet chosen as support
    z = np.empty(0, dtype=complex)   # support points (nodes)
    f = np.empty(0, dtype=complex)   # support values
    w = np.empty(0, dtype=complex)   # barycentric weights
    errvec: list[float] = []  # type: ignore
    support_indices: list[int] = []  # type: ignore

    # Initial: pick the point with largest |F|
    idx0 = int(np.argmax(np.abs(f_full)))
    support_indices.append(idx0)  # type: ignore
    z = np.append(z, z_full[idx0])
    f = np.append(f, f_full[idx0])
    J.remove(idx0)  # type: ignore

    r_approx = np.ones(M, dtype=complex) * f_full[idx0]  # rational approximant on all z_full  # type: ignore

    for _ in range(1, mmax + 1):
        # Residual on non-support points
        err = np.abs(f_full - r_approx)
        errvec.append(float(np.max(err)))  # type: ignore

        if errvec[-1] <= tol * sf:
            break

        # Select new support point: argmax residual
        J_arr = np.array(list(J))
        new_idx = int(J_arr[int(np.argmax(err[J_arr]))])
        support_indices.append(new_idx)  # type: ignore
        z = np.append(z, z_full[new_idx])
        f = np.append(f, f_full[new_idx])
        J.remove(new_idx)

        # Build Cauchy matrix C[i,j] = 1/(Z[i] - z[j]) for i in J_arr (updated)
        J_arr = np.array(list(J))
        z_j = z_full[J_arr]
        f_j = f_full[J_arr]
        C = 1.0 / (z_j[:, None] - z[None, :] + 1e-300)   # shape (|J|, m+1)

        # Loewner matrix: A[i,j] = (F[i] - f[j]) / (Z[i] - z[j])
        A = (f_j[:, None] - f[None, :]) * C       # shape (|J|, m+1)

        # Solve for weights via SVD: min ‖Aw‖ s.t. ‖w‖=1
        if A.shape[0] >= A.shape[1]:
            _, _, Vh = np.linalg.svd(A, full_matrices=True)
            w = Vh[-1, :].conj()
        else:
            # Underdetermined: least-norm solution
            _, _, Vh = np.linalg.svd(A, full_matrices=False)
            w = Vh[-1, :].conj()

        # Evaluate rational approximant on ALL z_full
        C_all = 1.0 / (z_full[:, None] - z[None, :] + 1e-300)  # shape (M, m+1)
        num = C_all @ (w * f)
        den = C_all @ w

        # Handle exact support points (den=0 not an issue; z_full[support] removed from J)
        r_approx = np.where(np.abs(den) > 1e-300, num / den, f_full)  # type: ignore

    # Compute poles: eigenvalues of companion-like matrix for denominator
    # The poles of the barycentric form are eigenvalues of the
    # generalized eigenproblem B*v = pole * E*v
    m_now = len(z)
    B = np.eye(m_now + 1, dtype=complex)
    B[0, 0] = 0.0
    E = np.zeros((m_now + 1, m_now + 1), dtype=complex)
    E[0, 1:] = w
    E[1:, 0] = np.ones(m_now)
    E[1:, 1:] = np.diag(z)
    try:
        from scipy.linalg import eig  # type: ignore
        eig_result = eig(E, B)  # type: ignore
        # eig returns either (eigenvalues, eigenvectors) or a single array
        # depending on parameters; extract eigenvalues safely
        if isinstance(eig_result, tuple):
            evals: np.ndarray = eig_result[0]  # type: ignore
        else:
            evals = eig_result  # type: ignore
        # Type safety: ensure evals is array-like
        evals = np.asarray(evals, dtype=complex)
        # Keep finite, non-NaN eigenvalues
        finite_mask = np.isfinite(evals) & (np.abs(evals) < 1e15)
        poles = evals[finite_mask]
    except Exception:
        poles = np.array([], dtype=complex)

    # Compute residues at poles via Cauchy formula
    residuals = np.zeros_like(poles)
    for k, pole in enumerate(poles):
        C_pole = 1.0 / (pole - z)
        den_deriv = np.sum(-w / (pole - z) ** 2)
        num_val = C_pole @ (w * f)
        if np.abs(den_deriv) > 1e-300:
            residuals[k] = num_val / den_deriv
        else:
            residuals[k] = np.nan

    return AAAResult(
        poles=poles,
        residuals=residuals,
        weights=w,
        nodes=z,
        values=f,
        err=errvec[-1] if errvec else float("inf"),
        support_indices=support_indices,
    )
