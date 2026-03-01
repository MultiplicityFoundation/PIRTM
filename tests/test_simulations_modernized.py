import numpy as np

from pirtm.simulations.qari_module import QARIEngine
from pirtm.simulations.quantum_feedback import QuantumFeedbackSimulator


def test_qari_engine_is_deterministic_with_seed():
    engine_a = QARIEngine(dim=4, Lambda_m=0.87, seed=7)
    engine_b = QARIEngine(dim=4, Lambda_m=0.87, seed=7)

    engine_a.evolve(steps=8)
    engine_b.evolve(steps=8)

    np.testing.assert_allclose(engine_a.get_final_state(), engine_b.get_final_state())
    assert len(engine_a.get_history()) == 9
    assert len(engine_b.get_history()) == 9


def test_qari_engine_entropy_and_phase_track_history_length():
    engine = QARIEngine(dim=3, Lambda_m=0.86, seed=11)
    engine.evolve(steps=6)

    entropy = engine.entropy_gradient()
    coherence = engine.phase_stability()

    assert len(entropy) == len(engine.get_history())
    assert len(coherence) == len(engine.get_history())
    assert all(np.isfinite(float(value)) for value in entropy)
    assert all(np.isfinite(float(value)) for value in coherence)


def test_quantum_feedback_simulator_is_deterministic_with_seed():
    sim_a = QuantumFeedbackSimulator(dim=3, num_primes=9, Lambda_m=0.85, seed=13)
    sim_b = QuantumFeedbackSimulator(dim=3, num_primes=9, Lambda_m=0.85, seed=13)

    sim_a.run(steps=7)
    sim_b.run(steps=7)

    np.testing.assert_allclose(sim_a.Xi, sim_b.Xi)
    assert len(sim_a.get_state_history()) == 8
    assert len(sim_b.get_state_history()) == 8
    assert len(sim_a.get_feedback_history()) == 7


def test_quantum_feedback_analysis_returns_stable_keys_without_plot():
    sim = QuantumFeedbackSimulator(dim=3, num_primes=7, Lambda_m=0.84, seed=17)
    sim.run(steps=5)

    analysis = sim.analyze_final_state(plot=False)

    assert set(analysis.keys()) >= {"eigvals", "eigvecs", "entropy", "coherence"}
    assert np.isfinite(float(analysis["entropy"]))
    assert np.isfinite(float(analysis["coherence"]))
