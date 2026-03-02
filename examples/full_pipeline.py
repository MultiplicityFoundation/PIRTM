import numpy as np

from pirtm import (
    PETCLedger,
    ace_certificate,
    build_gain_sequence,
    compute_margin,
    estimate_operator_norm,
    multi_step_margin,
    run,
    solve_budget,
    synthesize_weights,
    validate_schedule,
)


def main() -> None:
    dim = 4
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    def T(x: np.ndarray) -> np.ndarray:
        return 0.8 * x

    def P(x: np.ndarray) -> np.ndarray:
        return x

    x0 = np.ones(dim)

    op_norm, _ = estimate_operator_norm(T, dim=dim)
    budget = solve_budget(op_norm, epsilon=0.05, alpha=0.5)
    schedule = synthesize_weights(
        primes,
        dim=dim,
        op_norm_T=op_norm,
        q_star=budget.q_star,
        profile="log_decay",
        epsilon=0.05,
    )
    ok, max_q = validate_schedule(schedule, op_norm)

    gains = build_gain_sequence(len(primes), dim, profile="decay", scale=1e-3, seed=42)
    x_final, history, infos, status = run(
        x0,
        schedule.Xi_seq,
        schedule.Lam_seq,
        gains,
        T=T,
        P=P,
        epsilon=0.05,
        op_norm_T=op_norm,
    )

    cert = ace_certificate(infos)
    worst = multi_step_margin(infos)
    point_margin = compute_margin(infos[-1].nXi, infos[-1].nLam, op_norm, epsilon=infos[-1].epsilon)

    ledger = PETCLedger(min_length=3)
    for prime in primes[: len(infos)]:
        ledger.append(prime)
    petc_report = ledger.validate()

    print(
        {
            "schedule_valid": ok,
            "schedule_max_q": round(max_q, 6),
            "status_converged": status.converged,
            "status_safe": status.safe,
            "certificate": cert.certified,
            "certificate_margin": round(cert.margin, 6),
            "worst_margin": round(worst.margin, 6),
            "point_margin": round(point_margin.margin, 6),
            "petc_satisfied": petc_report.satisfied,
            "petc_coverage": round(petc_report.coverage, 6),
            "steps": status.steps,
            "history": len(history),
            "x_final_norm": round(float(np.linalg.norm(x_final)), 6),
        }
    )


if __name__ == "__main__":
    main()
