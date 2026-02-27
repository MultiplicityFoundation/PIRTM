import pickle

import numpy as np

from pirtm.weights import synthesize_weights, validate_schedule


def test_synthesize_shapes_and_length(small_primes):
    schedule = synthesize_weights(small_primes[:5], dim=4)
    assert len(schedule.Xi_seq) == 5
    assert all(x.shape == (4, 4) for x in schedule.Xi_seq)
    assert all(l.shape == (4, 4) for l in schedule.Lam_seq)


def test_validate_schedule_passes(small_primes):
    schedule = synthesize_weights(small_primes[:5], dim=4, op_norm_T=1.0, q_star=0.9)
    valid, max_q = validate_schedule(schedule, op_norm_T=1.0)
    assert valid is True
    assert max_q <= 0.9


def test_uniform_profile_constant_q_targets(small_primes):
    schedule = synthesize_weights(small_primes[:5], dim=3, profile="uniform")
    assert np.allclose(schedule.q_targets, schedule.q_targets[0])


def test_custom_profile(small_primes):
    schedule = synthesize_weights(small_primes[:4], dim=2, profile=lambda k, p: 0.3)
    valid, _ = validate_schedule(schedule, op_norm_T=1.0)
    assert valid is True


def test_weight_schedule_pickle_roundtrip(small_primes):
    schedule = synthesize_weights(small_primes[:3], dim=2)
    restored = pickle.loads(pickle.dumps(schedule))
    assert restored.primes_used == schedule.primes_used
