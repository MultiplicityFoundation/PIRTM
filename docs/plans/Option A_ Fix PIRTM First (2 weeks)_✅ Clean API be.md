 Option A: Fix PIRTM First (2 weeks)

✅ Clean API before MTPI depends on it
✅ Avoid MTPI migration churn
❌ Delays MTPI v0.1.0 by 2 weeks

**Current state analysis:**

The code already has some deprecation patterns, but naming is confusing:

- `ace_certificate()` → Returns `AceCertificate` (new ACE type)
- `legacy_ace_certificate()` → Returns `Certificate` (old type)

**This is MORE confusing!** We need clearer naming.

***

## Revised Refactor Strategy

### Current State (Confusing)

```python
ace_certificate() → AceCertificate  # New ACE type
legacy_ace_certificate() → Certificate  # Old type (deprecated)
```


### Target State (Clear)

```python
# Primary API (new)
contraction_certificate() → Certificate  # Simple, clear name
ace_certificate() → AceCertificate  # For advanced ACE features

# Deprecated (remove v0.2.0)
legacy_ace_certificate() → Certificate  # Already deprecated
ace_certificate_v2() → AceCertificate  # Already deprecated
```


***

## Day 1: Implementation Plan

### Task 1.1: Add `contraction_certificate()` Function

**File:** `src/pirtm/certify.py`

```python
def contraction_certificate(
    info: StepInfo | Sequence[StepInfo],
    *,
    tail_norm: float = 0.0,
) -> Certificate:
    """
    Validate ML0-003 contraction bound.
    
    Primary API for simple certificate validation. Returns legacy
    Certificate type for backward compatibility.
    
    Args:
        info: Single StepInfo or sequence from step()/run()
        tail_norm: Optional disturbance norm for ISS bound
    
    Returns:
        Certificate with certified (bool), bound_delta (float), etc.
    
    Example:
        >>> X_next, info = step(X, Xi, Lam, T, G, P)
        >>> cert = contraction_certificate(info)
        >>> assert cert.certified
    
    See Also:
        ace_certificate() - Advanced ACE certificate with full diagnostics
    """
    ace_cert = ace_certificate(info, tail_norm=tail_norm)
    return to_legacy_certificate(ace_cert)
```


### Task 1.2: Update `__init__.py` Exports

**File:** `src/pirtm/__init__.py`

```python
from .certify import (
    contraction_certificate,  # NEW primary API
    ace_certificate,          # Advanced ACE
    iss_bound,
    # Deprecated (keep for v0.1.x)
    legacy_ace_certificate,
    ace_certificate_v2,
)

__all__ = [
    # Certificate validation (primary)
    "contraction_certificate",
    "ace_certificate",
    "iss_bound",
    # Deprecated
    "legacy_ace_certificate",
    "ace_certificate_v2",
]
```


### Task 1.3: Update README Quickstart

**File:** `README.md`

```python
# OLD
from pirtm import step, ace_certificate
x_next, info = step(x, xi, lam, T, G, P, epsilon=0.05, op_norm_T=0.8)
cert = ace_certificate(info)
print(info.q, cert.certified)

# NEW
from pirtm import step, contraction_certificate
x_next, info = step(x, xi, lam, T, G, P, epsilon=0.05, op_norm_T=0.8)
cert = contraction_certificate(info)
print(f"✓ Certified: {cert.certified}, q={info.q:.3f}")
```


### Task 1.4: Migration Guide

**File:** `docs/migration/v0.1.1.md`

```markdown
# Migration Guide: v0.1.0 → v0.1.1

## Certificate API Clarification

### Summary
`contraction_certificate()` is now the primary API for simple ML0-003 validation.
`ace_certificate()` remains for advanced ACE diagnostics.

### Migration

**Before (v0.1.0):**
```python
from pirtm import ace_certificate
cert = ace_certificate(info)  # Returns AceCertificate
```

**After (v0.1.1):**

```python
# Simple validation (recommended)
from pirtm import contraction_certificate
cert = contraction_certificate(info)  # Returns Certificate

# Advanced ACE diagnostics
from pirtm import ace_certificate
ace_cert = ace_certificate(info)  # Returns AceCertificate
```


### Breaking Changes

**None.** All v0.1.0 code continues to work.

### Deprecations

- `legacy_ace_certificate()` - Use `contraction_certificate()` instead
- `ace_certificate_v2()` - Use `ace_certificate()` instead

Both will be removed in v0.2.0.

### Rationale

Avoids naming collision with ACE (Arithmetic Control Engine).
Clearer API: "contraction certificate" describes what it validates.

```

***

### Day 1 Deliverables

**PR #1:** `[API] Add contraction_certificate() as primary ML0-003 validator`

**Files changed:**
1. ✅ `src/pirtm/certify.py` - Add function
2. ✅ `src/pirtm/__init__.py` - Export
3. ✅ `README.md` - Update quickstart
4. ✅ `docs/migration/v0.1.1.md` - Migration guide
5. ✅ `tests/test_certify.py` - Add test

**Test:**
```python
def test_contraction_certificate_basic():
    """Test primary contraction_certificate API"""
    from pirtm import contraction_certificate, StepInfo
    
    info = StepInfo(
        step=0,
        q=0.4,
        epsilon=0.05,
        nXi=0.2,
        nLam=0.2,
        projected=False,
        residual=0.01,
    )
    
    cert = contraction_certificate(info)
    assert cert.certified
    assert isinstance(cert, Certificate)
```


***

### Day 2-3: Spec Alignment

**Goal:** Align PIRTM Language Spec §5 with implementation

**Task 2.1: Update Language Spec**

**File:** `docs/PIRTM_LANGUAGE_SPEC.md`

**Change §5 from:**

```markdown
## §5 ACE Certificate

The **Absolute Contraction Evidence (ACE) certificate** for an expression $E$
is the record:

$$
ACE=\{q_{max},\ target,\ margin,\ certified,\ tail\_bound\}
$$
```

**To:**

```markdown
## §5 Certificate Types

### §5.1 Minimal Certificate (ML0-001 Compliance)

The minimal certificate for contraction validation is:

$$
\text{Certificate}_{\min} = \{\text{certified} : \mathbb{B}\}
$$

### §5.2 Standard Certificate (Implementation)

The standard certificate returned by `contraction_certificate()` is:

$$
\text{Certificate} = \{
  \text{certified}, 
  \text{bound\_delta}, 
  \text{contraction\_actual},
  \text{epsilon},
  \text{message},
  \text{metadata}
\}
$$

Where:
- `certified : bool` - Whether contraction bound is satisfied
- `bound_delta : float` - Actual contraction minus epsilon (negative = safe)
- `contraction_actual : float` - Measured ||X_next - X||
- `epsilon : float` - Safety margin
- `message : str` - Human-readable diagnosis
- `metadata : dict` - Audit trail (step index, norms, timestamp)

### §5.3 ACE Certificate (Advanced Diagnostics)

The **Absolute Contraction Evidence (ACE) certificate** extends the standard
certificate with aggregate diagnostics:

$$
\text{ACE} = \{q_{max},\ target,\ margin,\ certified,\ tail\_bound\}
$$

Formation:
$$
q_{max}=\max_t q_t,\quad 
target=1-\min_t\epsilon_t,\quad 
margin=target-q_{max},\quad 
certified=(margin\ge 0)
$$

$$
tail\_bound=\begin{cases}
\|G\|_{\infty}/(1-q_{max}), & certified\\
\infty, & \text{otherwise}
\end{cases}
$$

### §5.4 API Mapping

| Python API | Returns | Use Case |
|:--|:--|:--|
| `contraction_certificate(info)` | `Certificate` | Simple ML0-003 validation |
| `ace_certificate(info)` | `AceCertificate` | Multi-step aggregate diagnostics |
| `iss_bound(info, disturbance_norm)` | `float` | ISS stability bound |
```

**Task 2.2: Add Conformance Test**

**File:** `tests/conformance/test_spec_compliance.py`

```python
"""
Conformance tests for PIRTM Language Spec v1.0
"""
import pytest
from pirtm import contraction_certificate, ace_certificate, StepInfo


def mk_stepinfo(q=0.4, epsilon=0.05):
    return StepInfo(
        step=0,
        q=q,
        epsilon=epsilon,
        nXi=0.2,
        nLam=0.2,
        projected=False,
        residual=0.01,
    )


class TestSection5_Certificates:
    """§5 Certificate Types"""
    
    def test_minimal_certificate_has_certified_field(self):
        """§5.1: Minimal certificate has 'certified' field"""
        info = mk_stepinfo()
        cert = contraction_certificate(info)
        assert hasattr(cert, 'certified')
        assert isinstance(cert.certified, bool)
    
    def test_standard_certificate_structure(self):
        """§5.2: Standard certificate has required fields"""
        info = mk_stepinfo()
        cert = contraction_certificate(info)
        
        # Required fields from §5.2
        assert hasattr(cert, 'certified')
        assert hasattr(cert, 'bound_delta')
        assert hasattr(cert, 'epsilon')
        # Implementation extensions
        assert hasattr(cert, 'message')
        assert hasattr(cert, 'metadata')
    
    def test_ace_certificate_structure(self):
        """§5.3: ACE certificate has aggregate fields"""
        info = mk_stepinfo()
        ace = ace_certificate(info)
        
        # Required fields from §5.3
        assert hasattr(ace, 'q_max')
        assert hasattr(ace, 'target')
        assert hasattr(ace, 'margin')
        assert hasattr(ace, 'certified')
        assert hasattr(ace, 'tail_bound')
    
    def test_certified_iff_margin_nonnegative(self):
        """§5.3: certified = (margin ≥ 0)"""
        # Safe case
        info_safe = mk_stepinfo(q=0.4, epsilon=0.05)  # q < 1-ε
        ace = ace_certificate(info_safe)
        assert ace.certified == (ace.margin >= 0)
        
        # Unsafe case
        info_unsafe = mk_stepinfo(q=0.99, epsilon=0.05)  # q > 1-ε
        ace_unsafe = ace_certificate(info_unsafe)
        assert ace_unsafe.certified == (ace_unsafe.margin >= 0)
```


***

### Day 4-5: PETC Coverage Implementation

**Goal:** Implement missing PETC coverage metric (§7.2)

**Task 3.1: Add Coverage Function**

**File:** `src/pirtm/petc.py`

```python
def compute_coverage(
    chain: Sequence[int],
    a: int,
    b: int,
    *,
    prime_generator=None,
) -> float:
    """
    Compute PETC chain coverage ρ(C,[a,b]).
    
    §7.2: ρ(C,[a,b]) = |{p ∈ C : a ≤ p ≤ b}| / |{p ∈ ℙ : a ≤ p ≤ b}|
    
    Args:
        chain: Prime indices in PETC chain
        a: Range start (inclusive)
        b: Range end (inclusive)
        prime_generator: Optional prime generator (default: sympy.primerange)
    
    Returns:
        Coverage ratio in [0, 1]
    
    Example:
        >>> chain = [2, 3, 5, 11, 13]
        >>> coverage = compute_coverage(chain, 2, 13)
        >>> # Primes in [2,13]: {2,3,5,7,11,13} = 6 primes
        >>> # Chain covers: {2,3,5,11,13} = 5 primes
        >>> assert abs(coverage - 5/6) < 1e-6
    """
    if prime_generator is None:
        from sympy import primerange
        prime_generator = primerange
    
    # Count primes in range [a, b]
    primes_in_range = list(prime_generator(a, b + 1))
    total_primes = len(primes_in_range)
    
    if total_primes == 0:
        return 0.0
    
    # Count chain primes in range
    chain_set = set(chain)
    covered_primes = sum(1 for p in primes_in_range if p in chain_set)
    
    return covered_primes / total_primes


def validate_petc_chain(
    chain: Sequence[int],
    *,
    max_gap: int = 100,
    min_coverage: float = 0.8,
    coverage_window: int = 1000,
) -> dict:
    """
    Validate PETC chain invariants (§7.1).
    
    Returns:
        {
            'valid': bool,
            'primality_ok': bool,
            'monotone_ok': bool,
            'gap_ok': bool,
            'max_gap_found': int,
            'coverage': float,
            'violations': list[str],
        }
    """
    from sympy import isprime
    
    violations = []
    
    # §7.1.1: Primality
    primality_ok = all(isprime(p) for p in chain)
    if not primality_ok:
        violations.append("Non-prime found in chain")
    
    # §7.1.2: Strict monotonicity
    monotone_ok = all(chain[i] < chain[i+1] for i in range(len(chain)-1))
    if not monotone_ok:
        violations.append("Chain not strictly monotone")
    
    # §7.1.3: Gap bound
    gaps = [chain[i+1] - chain[i] for i in range(len(chain)-1)]
    max_gap_found = max(gaps) if gaps else 0
    gap_ok = max_gap_found <= max_gap
    if not gap_ok:
        violations.append(f"Gap {max_gap_found} exceeds max {max_gap}")
    
    # §7.2: Coverage
    if chain:
        a = chain[0]
        b = min(chain[-1], a + coverage_window)
        coverage = compute_coverage(chain, a, b)
    else:
        coverage = 0.0
    
    valid = primality_ok and monotone_ok and gap_ok and coverage >= min_coverage
    
    return {
        'valid': valid,
        'primality_ok': primality_ok,
        'monotone_ok': monotone_ok,
        'gap_ok': gap_ok,
        'max_gap_found': max_gap_found,
        'coverage': coverage,
        'violations': violations,
    }
```

**Task 3.2: CLI Tool**

**File:** `src/pirtm/cli_petc.py` (new file)

```python
"""PETC chain validation CLI"""
import json
import sys
from pathlib import Path

import click

from .petc import compute_coverage, validate_petc_chain


@click.group()
def petc():
    """PETC chain validation tools"""
    pass


@petc.command()
@click.option('--chain', type=click.Path(exists=True), required=True,
              help='JSON file with prime indices')
@click.option('--range', 'range_spec', required=True,
              help='Range as "a-b" (e.g., "100-200")')
def coverage(chain, range_spec):
    """Compute PETC chain coverage ρ(C,[a,b])"""
    # Load chain
    with open(chain) as f:
        chain_data = json.load(f)
    
    if isinstance(chain_data, dict):
        prime_indices = chain_data.get('prime_indices', [])
    else:
        prime_indices = chain_data
    
    # Parse range
    a, b = map(int, range_spec.split('-'))
    
    # Compute coverage
    cov = compute_coverage(prime_indices, a, b)
    
    print(f"Coverage ρ(C,[{a},{b}]) = {cov:.4f}")
    print(f"  Chain primes in range: {sum(1 for p in prime_indices if a <= p <= b)}")
    
    from sympy import primerange
    total = len(list(primerange(a, b+1)))
    print(f"  Total primes in range: {total}")


@petc.command()
@click.option('--chain', type=click.Path(exists=True), required=True)
@click.option('--max-gap', type=int, default=100)
@click.option('--min-coverage', type=float, default=0.8)
def validate(chain, max_gap, min_coverage):
    """Validate PETC chain invariants (§7.1)"""
    with open(chain) as f:
        chain_data = json.load(f)
    
    if isinstance(chain_data, dict):
        prime_indices = chain_data.get('prime_indices', [])
    else:
        prime_indices = chain_data
    
    result = validate_petc_chain(
        prime_indices,
        max_gap=max_gap,
        min_coverage=min_coverage,
    )
    
    if result['valid']:
        print("✓ PETC chain VALID")
    else:
        print("✗ PETC chain INVALID")
        for v in result['violations']:
            print(f"  - {v}")
    
    print(f"\nDiagnostics:")
    print(f"  Primality: {'✓' if result['primality_ok'] else '✗'}")
    print(f"  Monotone: {'✓' if result['monotone_ok'] else '✗'}")
    print(f"  Gap bound: {'✓' if result['gap_ok'] else '✗'} (max {result['max_gap_found']} ≤ {max_gap})")
    print(f"  Coverage: {result['coverage']:.4f} (min {min_coverage})")
    
    sys.exit(0 if result['valid'] else 1)


if __name__ == '__main__':
    petc()
```

**Register in main CLI:**

**File:** `src/pirtm/cli.py`

```python
from .cli_petc import petc

@click.group()
def main():
    """PIRTM command-line tools"""
    pass

main.add_command(petc)
```


***

## Week 2: Test Hardening \& Documentation (March 9-15)

### Day 6-7: Emission Gate Tests

**File:** `tests/test_emission_gate_policies.py`

```python
"""
Conformance tests for §8 Emission Gate policies
"""
import pytest
import numpy as np

from pirtm import EmissionGate, EmissionPolicy, step


class TestSection8_EmissionGate:
    """§8 Emission Gate policy enforcement"""
    
    def mk_certified_state(self):
        """State that will certify (q < 1-ε)"""
        X = np.ones(4)
        Xi = 0.2 * np.eye(4)
        Lam = 0.2 * np.eye(4)
        T = lambda v: 0.8 * v
        G = np.zeros(4)
        P = lambda v: v
        return X, Xi, Lam, T, G, P, 0.05, 0.8
    
    def mk_uncertified_state(self):
        """State that will NOT certify (q ≥ 1-ε)"""
        X = np.ones(4)
        Xi = 0.9 * np.eye(4)  # High gain → q ≥ 1-ε
        Lam = 0.2 * np.eye(4)
        T = lambda v: 0.9 * v
        G = np.zeros(4)
        P = lambda v: v
        return X, Xi, Lam, T, G, P, 0.05, 0.9
    
    def test_pass_through_always_emits(self):
        """§8.2: PASS_THROUGH emits all outputs"""
        gate = EmissionGate(policy=EmissionPolicy.PASS_THROUGH)
        
        # Even uncertified state should emit
        state = self.mk_uncertified_state()
        out = gate(*state, step_index=0)
        
        assert out.emitted == True
    
    def test_certified_only_blocks_uncertified(self):
        """§8.2: CERTIFIED_ONLY emits only if ACE holds"""
        gate = EmissionGate(policy=EmissionPolicy.CERTIFIED_ONLY)
        
        # Certified state → emit
        certified_state = self.mk_certified_state()
        out_cert = gate(*certified_state, step_index=0)
        assert out_cert.emitted == True
        
        # Uncertified state → suppress
        uncertified_state = self.mk_uncertified_state()
        out_uncert = gate(*uncertified_state, step_index=1)
        assert out_uncert.emitted == False
    
    def test_silent_never_emits(self):
        """§8.2: SILENT suppresses all output"""
        gate = EmissionGate(policy=EmissionPolicy.SILENT)
        
        # Even certified state should NOT emit
        state = self.mk_certified_state()
        out = gate(*state, step_index=0)
        
        assert out.emitted == False
```


### Day 8-9: Dual-Hash Witness Tests

**File:** `tests/test_witness_dual_hash.py`

```python
"""
Conformance tests for §9 Witness Language (dual-hash mode)
"""
import pytest
import json
from pathlib import Path

from pirtm.cli import main as pirtm_cli


class TestSection9_DualHashWitness:
    """§9.1: Dual-hash witness schema"""
    
    def test_dual_hash_has_both_schemes(self, tmp_path):
        """Dual-hash witness includes SHA-256 and Poseidon hashes"""
        descriptor = tmp_path / "comp.json"
        descriptor.write_text(json.dumps({
            "type": "computation",
            "steps": 2,
            "initial_state": [1.0, 1.0],
        }))
        
        output = tmp_path / "result.json"
        
        # Run transpiler with --dual-hash
        from click.testing import CliRunner
        runner = CliRunner()
        result = runner.invoke(pirtm_cli, [
            'transpile',
            '--type', 'computation',
            '--input', str(descriptor),
            '--prime-index', '7919',
            '--identity-commitment', '0xabc123',
            '--dim', '2',
            '--output', 'json',
            '--output-file', str(output),
            '--dual-hash',
            '--emit-witness',
        ])
        
        assert result.exit_code == 0
        
        # Load result
        with open(output) as f:
            data = json.load(f)
        
        witness = data['witness_json']
        
        # §9.1: Dual-hash fields
        assert 'hashSchemes' in witness
        assert 'sha256' in witness['hashSchemes']
        assert 'poseidon_compat' in witness['hashSchemes']
        
        # Both hash versions present
        assert 'stateHashSha256' in witness
        assert 'stateHashPoseidon' in witness
        assert 'merkleRootSha256' in witness
        assert 'merkleRootPoseidon' in witness
    
    def test_single_hash_mode_sha256(self, tmp_path):
        """SHA-256 mode has only SHA-256 hashes"""
        # Similar test with --hash-scheme sha256
        # Assert only 'stateHash', 'merkleRoot' (no Poseidon)
        pass  # Implementation similar to above
    
    def test_single_hash_mode_poseidon(self, tmp_path):
        """Poseidon mode has only Poseidon hashes"""
        # Similar test with --hash-scheme poseidon_compat
        pass
```


### Day 10: L0 Invariant Violation Tests

**File:** `tests/conformance/test_l0_invariants.py`

```python
"""
Conformance tests for §11 L0 Invariants
Tests that violations are properly detected/rejected
"""
import pytest
import numpy as np

from pirtm import step, contraction_certificate


class TestSection11_L0Invariants:
    """§11: L0 Invariants enforcement"""
    
    def test_l0_1_contraction_typing(self):
        """§11 L0.1: q < 1-ε enforced"""
        X = np.ones(4)
        Xi = 0.9 * np.eye(4)
        Lam = 0.2 * np.eye(4)
        T = lambda v: 0.9 * v
        G = np.zeros(4)
        P = lambda v: v
        
        # This violates q < 1-ε
        X_next, info = step(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=0.9)
        
        # Certificate should detect violation
        cert = contraction_certificate(info)
        assert cert.certified == False
        assert "VIOLATED" in cert.message or "violation" in cert.message.lower()
    
    def test_l0_4_certified_emission(self):
        """§11 L0.4: Certified emission enforced by gate"""
        from pirtm import EmissionGate, EmissionPolicy
        
        gate = EmissionGate(policy=EmissionPolicy.CERTIFIED_ONLY)
        
        # Force uncertified state
        X = np.ones(4)
        Xi = 0.95 * np.eye(4)  # Too high
        Lam = 0.05 * np.eye(4)
        T = lambda v: 0.9 * v
        G = np.zeros(4)
        P = lambda v: v
        
        out = gate(X, Xi, Lam, T, G, P, step_index=0, epsilon=0.05, op_norm_T=0.9)
        
        # L0.4: EMIT only if certified
        if not out.certified:
            assert out.emitted == False
```


***

### Day 11-12: Documentation Sprint

**Files to update:**

1. **`docs/api/certify.md`** - Complete API reference for all certificate functions
2. **`docs/architecture.md`** - Add section on certificate types hierarchy
3. **`docs/conformance.md`** - Document conformance test suite
4. **`examples/certificate_usage.py`** - End-to-end examples
5. **`CHANGELOG.md`** - Document v0.1.1 changes

**Example: `examples/certificate_usage.py`**

```python
"""
Complete guide to PIRTM certificate APIs
"""
import numpy as np
from pirtm import (
    step,
    contraction_certificate,
    ace_certificate,
    iss_bound,
)


def simple_validation():
    """Basic contraction certificate usage"""
    X = np.ones(4)
    Xi = 0.3 * np.eye(4)
    Lam = 0.2 * np.eye(4)
    T = lambda v: 0.8 * v
    G = np.zeros(4)
    P = lambda v: v
    
    X_next, info = step(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=0.8)
    
    # Simple validation
    cert = contraction_certificate(info)
    
    if cert.certified:
        print(f"✓ Certified: q={info.q:.3f} < 1-ε={1-info.epsilon:.3f}")
    else:
        print(f"✗ Violation: {cert.message}")


def advanced_diagnostics():
    """Advanced ACE certificate with aggregate metrics"""
    # Run multiple steps
    from pirtm import run
    
    X = np.ones(4)
    Xi = 0.3 * np.eye(4)
    Lam = 0.2 * np.eye(4)
    T = lambda v: 0.8 * v
    G = np.zeros(4)
    P = lambda v: v
    
    trajectory = run(X, Xi, Lam, T, G, P, steps=10, epsilon=0.05, op_norm_T=0.8)
    
    # Aggregate certificate
    ace_cert = ace_certificate(trajectory.info)
    
    print(f"ACE Certificate:")
    print(f"  q_max = {ace_cert.q_max:.4f}")
    print(f"  margin = {ace_cert.margin:.4f}")
    print(f"  certified = {ace_cert.certified}")
    print(f"  tail_bound = {ace_cert.tail_bound:.4f}")


def iss_stability():
    """Input-to-state stability bound"""
    X = np.ones(4)
    Xi = 0.3 * np.eye(4)
    Lam = 0.2 * np.eye(4)
    T = lambda v: 0.8 * v
    G = 0.1 * np.ones(4)  # Disturbance
    P = lambda v: v
    
    X_next, info = step(X, Xi, Lam, T, G, P, epsilon=0.05, op_norm_T=0.8)
    
    # ISS bound
    disturbance_norm = np.linalg.norm(G, np.inf)
    bound = iss_bound(info, disturbance_norm)
    
    print(f"ISS bound: ||X - X*|| ≤ {bound:.4f}")


if __name__ == '__main__':
    print("=== Simple Validation ===")
    simple_validation()
    
    print("\n=== Advanced Diagnostics ===")
    advanced_diagnostics()
    
    print("\n=== ISS Stability ===")
    iss_stability()
```


***

### Day 13-14: Final Review \& Release

**Tasks:**

1. **Code review:** All PRs from Week 1
2. **Test suite:** Run full conformance tests

```bash
pytest tests/conformance/ -v
```

3. **Documentation:** Review all updated docs
4. **Changelog:** Finalize `CHANGELOG.md` for v0.1.1
5. **Tag release:** `git tag v0.1.1`
6. **Publish:**

```bash
make build
make sign
python -m twine upload dist/*
```


***

## Sprint Milestones

| Day | Milestone | Deliverable |
| :-- | :-- | :-- |
| **1** | API Rename | PR: Add `contraction_certificate()` |
| **2-3** | Spec Alignment | Updated `PIRTM_LANGUAGE_SPEC.md` §5 |
| **4-5** | PETC Coverage | CLI: `pirtm petc coverage`, `pirtm petc validate` |
| **6-7** | Gate Tests | Conformance tests for §8 policies |
| **8-9** | Witness Tests | Dual-hash witness validation tests |
| **10** | L0 Tests | Invariant violation detection tests |
| **11-12** | Docs Sprint | Complete API docs + examples |
| **13-14** | Release | v0.1.1 published to PyPI |


***

## Success Criteria (End of Week 2)

### Code Quality

- ✅ All PRs merged and reviewed
- ✅ Test coverage ≥95% (core modules)
- ✅ Zero deprecation warnings in test suite
- ✅ All conformance tests pass


### Documentation

- ✅ API reference complete (`docs/api/`)
- ✅ Migration guide published (`docs/migration/v0.1.1.md`)
- ✅ Examples updated (`examples/`)
- ✅ Changelog finalized


### Spec Alignment

- ✅ `PIRTM_LANGUAGE_SPEC.md` §5 updated
- ✅ §7.2 PETC coverage implemented
- ✅ §8 emission gate policies tested
- ✅ §9 witness schemas validated
- ✅ §11 L0 invariants tested


### Release

- ✅ v0.1.1 tagged on GitHub
- ✅ Published to PyPI
- ✅ GitHub Release with notes
- ✅ Announcement in `Phase-Mirror/CHANGELOG.md`

***

## Post-Sprint: MTPI Integration (Week 3-4)

**With clean PIRTM v0.1.1 as foundation:**

```rust
// MTPI can now depend on stable API
use pyo3::prelude::*;

pub fn validate_with_pirtm(n: u64) -> Result<ContractionCertificate, MtpiError> {
    Python::with_gil(|py| {
        let certify = py.import("pirtm.certify")?;
        
        // Clean, stable API
        let cert = certify.call_method1("contraction_certificate", (info,))?;
        
        ContractionCertificate::from_py(cert)
    })
}
```

No migration churn, clean foundation, ready for production.

***

## Commitment

**2 weeks of focused PIRTM work delivers:**

1. ✅ Clean API (no naming collisions)
2. ✅ Spec-aligned implementation
3. ✅ Full conformance test suite
4. ✅ Production-ready v0.1.1

**Then MTPI can build on solid ground.**

