from pirtm.infinite_prime import infinite_prime_check


def test_empty_input():
    out = infinite_prime_check([])
    assert out["ok"] is False
    assert out["reason"] == "no primes"


def test_dense_primes_ok():
    out = infinite_prime_check([2, 3, 5, 7, 11], min_density=0.3)
    assert out["ok"] is True
    assert out["count"] == 5


def test_duplicates_and_filtering():
    out = infinite_prime_check([1, 2, 2, 3, 4, 5])
    assert out["support"] == [2, 3, 5]
    assert out["count"] == 3
