import numpy as np

from pirtm import ace_certificate, run, step


def main() -> None:
    dim = 4
    x0 = np.ones(dim)
    xi = 0.3 * np.eye(dim)
    lam = 0.2 * np.eye(dim)

    def T(x: np.ndarray) -> np.ndarray:
        return 0.8 * x

    g = np.zeros(dim)

    def P(x: np.ndarray) -> np.ndarray:
        return x

    x1, info = step(x0, xi, lam, T, g, P, epsilon=0.05, op_norm_T=0.8)
    cert = ace_certificate(info)
    print(f"single-step q={info.q:.4f}, certified={cert.certified}")

    n = 20
    xi_seq = [xi] * n
    lam_seq = [lam] * n
    g_seq = [g] * n
    x_final, history, infos, status = run(
        x0,
        xi_seq,
        lam_seq,
        g_seq,
        T=T,
        P=P,
        epsilon=0.05,
        op_norm_T=0.8,
    )
    cert2 = ace_certificate(infos)
    print(
        "run",
        f"steps={status.steps}",
        f"converged={status.converged}",
        f"safe={status.safe}",
        f"margin={cert2.margin:.4f}",
        f"tail={cert2.tail_bound:.6f}",
        f"history={len(history)}",
        f"x_final_norm={np.linalg.norm(x_final):.6f}",
    )


if __name__ == "__main__":
    main()
