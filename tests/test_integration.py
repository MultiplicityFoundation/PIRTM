import numpy as np

from pirtm import (
    PETCLedger,
    ace_certificate,
    build_gain_sequence,
    estimate_operator_norm,
    multi_step_margin,
    run,
    solve_budget,
    synthesize_weights,
    validate_schedule,
)


def test_full_pipeline_converges(small_primes):
    dim = 4
    T = lambda x: 0.8 * x
    P = lambda x: x
    x0 = np.ones(dim)

    op_norm, _ = estimate_operator_norm(T, dim=dim)
    budget = solve_budget(op_norm_T=op_norm, epsilon=0.05)
    schedule = synthesize_weights(small_primes[:10], dim=dim, op_norm_T=op_norm, q_star=budget.q_star)
    valid, _ = validate_schedule(schedule, op_norm)
    assert valid

    gains = build_gain_sequence(10, dim, profile="decay", scale=0.001, seed=42)
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
    assert len(history) == len(infos) + 1
    cert = ace_certificate(infos)
    margin = multi_step_margin(infos)
    assert cert.certified
    assert margin.safe

    ledger = PETCLedger(min_length=3)
    for prime in small_primes[: len(infos)]:
        ledger.append(prime)
    report = ledger.validate()
    assert report.satisfied is True
