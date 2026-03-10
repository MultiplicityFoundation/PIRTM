"""
Test Suite for PIRTM Dialect Types

ADR-006: Dialect Type-Layer Gate (Day 0-3)

This test suite validates:
  - Test 1: Prime cert (PASS)
  - Test 2: Non-prime composite cert via non-prime (FAIL)
  - Test 3: Non-squarefree composite cert via perfect square (FAIL)
  - Test 4: Valid session graph with squarefree mod (PASS)

Run with: pytest pirtm/tests/test_dialect_types.py -v
"""

import pytest
from pirtm.dialect.pirtm_types import (
    CertType,
    EpsilonType,
    OpNormTType,
    SessionGraphType,
    CouplingType,
    VerificationError,
    create_cert,
    create_epsilon,
    create_op_norm_t,
    create_session_graph,
    is_prime,
    factorize,
)


# ===== Test 1: Prime Cert (PASS) =====

def test_cert_prime_7_passes():
    """
    Test 1: !pirtm.cert(mod=7) should successfully verify.
    
    7 is prime, so certification should succeed.
    """
    cert = create_cert(mod=7)
    assert cert.mod == 7
    assert str(cert) == "!pirtm.cert(mod=7)"
    print("✅ Test 1 PASS: !pirtm.cert(mod=7) verified (7 is prime)")


# ===== Test 2: Non-Prime Composite (FAIL) =====

def test_cert_composite_7921_fails_with_factorization():
    """
    Test 2: !pirtm.cert(mod=7921) should fail with error showing factorization.
    
    7921 = 89 * 89 (perfect square), not prime.
    
    Expected error message must include:
      - "mod=7921 is not prime"
      - "89 * 89" or "89^2"
    """
    with pytest.raises(VerificationError) as excinfo:
        create_cert(mod=7921)
    
    error_msg = str(excinfo.value)
    
    # Verify error message includes mod value
    assert "mod=7921" in error_msg, f"Error message missing mod=7921: {error_msg}"
    
    # Verify error message indicates non-prime
    assert "is not prime" in error_msg, f"Error message missing 'is not prime': {error_msg}"
    
    # Verify factorization is shown
    assert "89" in error_msg, f"Error message missing factorization (89): {error_msg}"
    
    print(f"✅ Test 2 PASS: !pirtm.cert(mod=7921) correctly rejected")
    print(f"   Error: {error_msg}")


# ===== Test 3: Non-Squarefree Composite (FAIL) =====

def test_cert_perfect_square_49_fails_with_factorization():
    """
    Test 3: !pirtm.cert(mod=49) should fail with error showing factorization.
    
    49 = 7^2 (perfect square), not prime.
    
    Expected error message must include:
      - "mod=49 is not prime"
      - "7^2" or "7 * 7"
    """
    with pytest.raises(VerificationError) as excinfo:
        create_cert(mod=49)
    
    error_msg = str(excinfo.value)
    
    # Verify error message includes mod value
    assert "mod=49" in error_msg, f"Error message missing mod=49: {error_msg}"
    
    # Verify error message indicates non-prime
    assert "is not prime" in error_msg, f"Error message missing 'is not prime': {error_msg}"
    
    # Verify factorization is shown
    assert "7" in error_msg, f"Error message missing factorization (7): {error_msg}"
    
    print(f"✅ Test 3 PASS: !pirtm.cert(mod=49) correctly rejected")
    print(f"   Error: {error_msg}")


# ===== Test 4: Squarefree Session Graph (PASS) =====

def test_session_graph_squarefree_6_passes():
    """
    Test 4: !pirtm.session_graph(mod=6, coupling=#pirtm.unresolved_coupling) 
    should successfully verify.
    
    6 = 2 * 3 is squarefree (no repeated prime factors).
    Coupling is unresolved as required at transpile time.
    """
    sg = create_session_graph(mod=6, coupling=CouplingType.UNRESOLVED)
    assert sg.mod == 6
    assert sg.coupling == CouplingType.UNRESOLVED
    assert str(sg) == "!pirtm.session_graph(mod=6, coupling=#pirtm.unresolved_coupling)"
    print("✅ Test 4 PASS: !pirtm.session_graph(mod=6, coupling=#pirtm.unresolved_coupling) verified (6 is squarefree)")


# ===== Additional Coverage Tests =====

def test_epsilon_type_with_valid_prime():
    """Epsilon type should accept prime modulus."""
    eps = create_epsilon(mod=11, value=0.05)
    assert eps.mod == 11
    assert eps.value == 0.05
    print("✅ Epsilon(mod=11, value=0.05) created successfully")


def test_epsilon_type_rejects_non_prime():
    """Epsilon type should reject non-prime modulus."""
    with pytest.raises(VerificationError) as excinfo:
        create_epsilon(mod=15, value=0.05)  # 15 = 3 * 5
    
    assert "is not prime" in str(excinfo.value)
    print("✅ Epsilon(mod=15) correctly rejected (15 = 3 * 5)")


def test_op_norm_t_with_valid_prime():
    """OpNormT type should accept prime modulus."""
    ont = create_op_norm_t(mod=13, norm=2.5)
    assert ont.mod == 13
    assert ont.norm == 2.5
    print("✅ OpNormT(mod=13, norm=2.5) created successfully")


def test_op_norm_t_rejects_negative_norm():
    """OpNormT type should reject negative norm."""
    with pytest.raises(VerificationError) as excinfo:
        create_op_norm_t(mod=7, norm=-1.0)
    
    assert "negative" in str(excinfo.value)
    print("✅ OpNormT(mod=7, norm=-1.0) correctly rejected (negative norm)")


def test_session_graph_rejects_non_squarefree():
    """SessionGraph should reject non-squarefree modulus."""
    # 4 = 2^2 is not squarefree
    with pytest.raises(VerificationError) as excinfo:
        create_session_graph(mod=4, coupling=CouplingType.UNRESOLVED)
    
    error_msg = str(excinfo.value)
    assert "mod=4" in error_msg
    assert "not squarefree" in error_msg
    assert "2^2" in error_msg or "2 \\* 2" in error_msg
    print("✅ SessionGraph(mod=4) correctly rejected (4 = 2^2 is not squarefree)")


# ===== Miller-Rabin Verification Tests =====

def test_is_prime_small_primes():
    """Miller-Rabin should correctly identify small primes."""
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in primes:
        assert is_prime(p), f"Miller-Rabin failed to recognize {p} as prime"
    print(f"✅ Miller-Rabin correctly identifies {len(primes)} small primes")


def test_is_prime_small_composites():
    """Miller-Rabin should correctly reject small composites."""
    composites = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25]
    for c in composites:
        assert not is_prime(c), f"Miller-Rabin incorrectly identified {c} as prime"
    print(f"✅ Miller-Rabin correctly rejects {len(composites)} small composites")


def test_is_prime_large_primes():
    """Miller-Rabin should correctly identify large primes."""
    large_primes = [1009, 10007, 100003, 1000003]
    for p in large_primes:
        assert is_prime(p), f"Miller-Rabin failed on large prime {p}"
    print(f"✅ Miller-Rabin correctly identifies {len(large_primes)} large primes")


def test_is_prime_large_composites():
    """Miller-Rabin should correctly reject large composites."""
    large_composites = [1000, 10001, 100000, 1000000]
    for c in large_composites:
        assert not is_prime(c), f"Miller-Rabin incorrectly identified {c} as prime"
    print(f"✅ Miller-Rabin correctly rejects {len(large_composites)} large composites")


# ===== Factorization Tests =====

def test_factorize_prime():
    """Factorization of prime should be the prime itself."""
    assert factorize(7) == "7"
    assert factorize(11) == "11"
    print("✅ Factorization correctly handles primes")


def test_factorize_composite_squarefree():
    """Factorization of squarefree composite should list distinct primes."""
    result = factorize(6)  # 2 * 3
    assert "2" in result
    assert "3" in result
    print(f"✅ Factorization(6) = {result} (squarefree)")


def test_factorize_composite_non_squarefree():
    """Factorization of non-squarefree composite should show exponents."""
    result = factorize(49)  # 7^2
    assert "7^2" in result or "7 \\* 7" in result
    
    result = factorize(12)  # 2^2 * 3
    assert "2^2" in result
    assert "3" in result
    print(f"✅ Factorization handles non-squarefree composites with exponents")


# ===== Day 0-3 Gate Acceptance =====

def test_day_0_3_gate_all_four_cases():
    """
    ADR-006 Day 0-3 Acceptance Test
    
    All four test cases must pass:
    1. Prime cert (pass)
    2. Non-prime composite (fail with factorization)
    3. Non-squarefree composite (fail with factorization)
    4. Squarefree session graph (pass)
    """
    print("\n" + "="*60)
    print("ADR-006 Day 0-3 Gate: Dialect Type-Layer Verification")
    print("="*60)
    
    # Test 1
    test_cert_prime_7_passes()
    
    # Test 2
    test_cert_composite_7921_fails_with_factorization()
    
    # Test 3
    test_cert_perfect_square_49_fails_with_factorization()
    
    # Test 4
    test_session_graph_squarefree_6_passes()
    
    print("="*60)
    print("✅ DAY 0-3 GATE: ALL FOUR TEST CASES PASSED")
    print("="*60)


if __name__ == "__main__":
    # Run the day 0-3 gate test
    test_day_0_3_gate_all_four_cases()
    
    # Run all tests
    print("\n\nRunning full test suite with pytest...")
    pytest.main([__file__, "-v"])
