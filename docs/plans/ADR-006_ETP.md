<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Lets create development blueprints, file scaffold, and test harness for ace protocol and petc module for PIRTM.

Now I have the live code. The critical fact: [`certify.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/9f84185e02b285595b293cfb9c3408401a498980/src/pirtm/certify.py) is a **30-line shim** covering L0-heuristic only, and [`petc.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/9f84185e02b285595b293cfb9c3408401a498980/src/pirtm/petc.py) is a working ledger with no Merkle/signature arithmetic.  The gap is everything from L1 through L5 certification levels and the PETC→ACE coupling that ETP's Static Tail depends on.  Here is the full blueprint.

***

## Central Tensions

- **Completeness vs. TRL honesty** — ACE L0 (heuristic) is TRL-2; L2 (power iteration) is TRL-3; L5 (external-verified) is TRL-4+. All must be labeled. Shipping them in the same module without annotations invites IP contamination of patent claims.
- **PETC as ledger vs. PETC as provenance primitive** — the existing `PETCLedger` appends entries; it does not produce Merkle roots, chain `prevHash` links, or prime-exponent vector signatures. ETP's Jubilee checkpoint requires all three.
- **`certify.py` as public API surface vs. internal implementation** — the shim is currently imported directly by `petc_bridge.py`. Moving to an `ace/` sub-package must preserve the public import path `from pirtm.certify import ace_certificate`.

***

## File Scaffold

```text
PIRTM/
└── src/pirtm/
    │
    ├── petc.py                        ← EXISTING — keep as public shim, re-export from petc/
    ├── certify.py                     ← EXISTING — keep as public shim, re-export from ace/
    ├── petc_bridge.py                 ← EXISTING — no changes required
    │
    ├── ace/                           ← NEW sub-package
    │   ├── __init__.py                ← re-exports ace_certificate, iss_bound, AceProtocol
    │   ├── protocol.py                ← AceProtocol: dispatch to level-specific certifiers
    │   ├── budget.py                  ← AceBudget: τ tracker, depletion-rate guard
    │   ├── witness.py                 ← AceWitness: production artifact for ETP Static Tail
    │   ├── levels/
    │   │   ├── __init__.py
    │   │   ├── l0_heuristic.py        ← existing certify.py logic, TRL-2
    │   │   ├── l1_normbound.py        ← ‖K‖ ≤ Σ bₚ|wₚ| weighted-ℓ₁ sum, TRL-2
    │   │   ├── l2_poweriter.py        ← power iteration for tighter ρ(K), TRL-3
    │   │   ├── l3_nonexpansive.py     ← non-expansive clamp projection, TRL-3
    │   │   └── l4_perturbation.py     ← perturbation budget bound, TRL-4
    │   └── types.py                   ← AceCertificate, CertLevel, AceBudgetState
    │
    ├── petc/                          ← NEW sub-package (expands petc.py)
    │   ├── __init__.py                ← re-exports PETCLedger, petc_invariants
    │   ├── ledger.py                  ← PETCLedger moved here verbatim
    │   ├── signature.py               ← prime-exponent vector arithmetic (PETC signatures)
    │   ├── chain.py                   ← prevHash-linked chain with SHA-256 atomId
    │   └── merkle.py                  ← Jubilee Merkle root builder
    │
    └── tests/                         ← (relative to repo root: tests/)
        ├── test_petc.py               ← EXISTING (1248 bytes) — will be expanded
        ├── test_petc_bridge.py        ← EXISTING — no changes
        ├── test_certify.py            ← EXISTING (1188 bytes) — will be expanded
        │
        ├── test_ace_protocol.py       ← NEW: full multi-level ACE harness
        ├── test_ace_budget.py         ← NEW: budget τ, depletion-rate guard
        ├── test_ace_witness.py        ← NEW: witness production for ETP coupling
        ├── test_petc_signature.py     ← NEW: prime-exponent vector arithmetic
        ├── test_petc_chain.py         ← NEW: prevHash chain integrity
        ├── test_petc_merkle.py        ← NEW: Jubilee Merkle root
        └── test_ace_petc_coupling.py  ← NEW: ACE certification emits PETC entry
```


***

## ACE Sub-Package — Full Implementations

### `src/pirtm/ace/types.py`

```python
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CertLevel(str, Enum):
    """TRL mapping: L0=TRL-2, L1=TRL-2, L2=TRL-3, L3=TRL-3, L4=TRL-4."""
    L0_HEURISTIC        = "L0-heuristic"
    L1_NORMBOUND        = "L1-normbound"
    L2_POWERITER        = "L2-poweriter"
    L3_NONEXPANSIVE     = "L3-nonexpansive-clamp"
    L4_PERTURBATION     = "L4-perturbation-budget"

    @property
    def trl(self) -> int:
        return {
            "L0-heuristic": 2,
            "L1-normbound": 2,
            "L2-poweriter": 3,
            "L3-nonexpansive-clamp": 3,
            "L4-perturbation-budget": 4,
        }[self.value]


@dataclass(frozen=True)
class AceCertificate:
    """
    Machine-checkable contraction certificate.
    Mirrors ContractionCertificate in packages/guardian/src/types/etp-types.ts.
    """
    level:           CertLevel
    certified:       bool
    lipschitz_upper: float          # ‖K‖ upper bound
    gap_lb:          float          # 1 − ‖K‖ (must be > 0 when certified=True)
    contraction_rate: float         # ‖K‖ (same as lipschitz_upper for this impl)
    budget_used:     float          # Σ bₚ |wₚ|
    tau:             float          # ACE budget τ
    delta:           float          # safety margin = gap_lb − δ_threshold
    margin:          float          # target − max_q (legacy compat with certify.py)
    tail_bound:      float          # ISS tail bound
    details:         dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.certified and self.gap_lb <= 0:
            raise ValueError(
                f"AceCertificate.certified=True requires gap_lb > 0, "
                f"got {self.gap_lb}"
            )
        if self.lipschitz_upper < 0:
            raise ValueError("lipschitz_upper must be ≥ 0")


@dataclass
class AceBudgetState:
    tau:            float = 1.0    # total budget
    consumed:       float = 0.0   # Σ bₚ |wₚ| so far
    depletion_rate: float = 0.0   # per-cycle consumption rate

    @property
    def remaining(self) -> float:
        return max(0.0, self.tau - self.consumed)

    @property
    def is_depleted(self) -> bool:
        return self.consumed >= self.tau
```


### `src/pirtm/ace/budget.py`

```python
from __future__ import annotations
from .types import AceBudgetState

MAX_DEPLETION_RATE = 0.01  # L0 invariant: depletion rate < 0.01/cycle


class AceBudget:
    """
    Tracks ACE budget τ consumption across certification calls.
    L0 invariant: depletion_rate < MAX_DEPLETION_RATE per cycle.
    Violation raises — never silently continues.
    """

    def __init__(self, tau: float = 1.0) -> None:
        if tau <= 0:
            raise ValueError("tau must be > 0")
        self._state = AceBudgetState(tau=tau)
        self._cycle_start_consumed: float = 0.0

    def consume(self, amount: float) -> AceBudgetState:
        if amount < 0:
            raise ValueError("budget consumption must be ≥ 0")
        self._state.consumed += amount
        self._state.depletion_rate = amount  # last consumption as rate proxy
        if self._state.depletion_rate >= MAX_DEPLETION_RATE * self._state.tau:
            raise RuntimeError(
                f"ACE_BUDGET_DEPLETION_RATE_EXCEEDED: {self._state.depletion_rate:.6f} "
                f">= {MAX_DEPLETION_RATE * self._state.tau:.6f}. "
                "L0 invariant violated — execution halted."
            )
        if self._state.is_depleted:
            raise RuntimeError(
                f"ACE_BUDGET_DEPLETED: consumed={self._state.consumed:.4f} "
                f">= tau={self._state.tau:.4f}"
            )
        return self._state

    def snapshot(self) -> AceBudgetState:
        return AceBudgetState(
            tau=self._state.tau,
            consumed=self._state.consumed,
            depletion_rate=self._state.depletion_rate,
        )

    def reset_cycle(self) -> None:
        self._cycle_start_consumed = self._state.consumed
```


### `src/pirtm/ace/levels/l0_heuristic.py`

```python
"""
L0-heuristic: TRL-2. Wraps existing certify.ace_certificate logic exactly.
Use for development scaffolding only — not for patent claim bodies.
"""
from __future__ import annotations
from typing import Sequence
from pirtm.types import StepInfo
from ..types import AceCertificate, CertLevel


def certify_l0(
    records: Sequence[StepInfo],
    *,
    tau: float = 1.0,
    tail_norm: float = 0.0,
    delta: float = 0.05,
) -> AceCertificate:
    if not records:
        raise ValueError("L0: no telemetry provided")

    target = 1.0 - min(r.epsilon for r in records)
    max_q = max(r.q for r in records)
    margin = target - max_q
    certified = margin >= delta
    lipschitz_upper = max_q
    gap_lb = 1.0 - lipschitz_upper

    tail_bound = (
        float("inf") if max_q >= 1.0
        else tail_norm / max(1e-12, 1.0 - max_q)
    )
    budget_used = sum(abs(getattr(r, "w", 0.0)) for r in records)

    return AceCertificate(
        level=CertLevel.L0_HEURISTIC,
        certified=certified,
        lipschitz_upper=lipschitz_upper,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=max_q,
        budget_used=budget_used,
        tau=tau,
        delta=delta,
        margin=margin,
        tail_bound=tail_bound,
        details={"max_q": max_q, "target": target, "steps": len(records)},
    )
```


### `src/pirtm/ace/levels/l1_normbound.py`

```python
"""
L1-normbound: TRL-2. ‖K‖ ≤ Σ bₚ |wₚ| — weighted-ℓ₁ norm bound.
This is the bound that ETP's ℓ_safe derivation depends on (ADR-001).
"""
from __future__ import annotations
import numpy as np
from typing import Sequence
from ..types import AceCertificate, CertLevel


def certify_l1(
    weights: Sequence[float],
    basis_norms: Sequence[float],
    *,
    tau: float = 1.0,
    delta: float = 0.05,
) -> AceCertificate:
    """
    weights:     w_p coefficients in K = Σ_p w_p B_p
    basis_norms: ‖B_p‖ for each prime-indexed basis operator
    """
    if len(weights) != len(basis_norms):
        raise ValueError("weights and basis_norms must have equal length")
    if not weights:
        raise ValueError("L1: empty weight/norm vectors")

    lipschitz_upper = float(sum(abs(w) * b for w, b in zip(weights, basis_norms)))
    budget_used = lipschitz_upper
    gap_lb = 1.0 - lipschitz_upper
    certified = lipschitz_upper < (1.0 - delta)

    return AceCertificate(
        level=CertLevel.L1_NORMBOUND,
        certified=certified,
        lipschitz_upper=lipschitz_upper,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=lipschitz_upper,
        budget_used=budget_used,
        tau=tau,
        delta=delta,
        margin=gap_lb - delta,
        tail_bound=float("inf") if lipschitz_upper >= 1.0 else tau / max(1e-12, gap_lb),
        details={
            "weights": list(weights),
            "basis_norms": list(basis_norms),
            "n_operators": len(weights),
        },
    )
```


### `src/pirtm/ace/levels/l2_poweriter.py`

```python
"""
L2-poweriter: TRL-3. Power iteration for tighter spectral radius ρ(K).
Resolves ADR-001 open precision question: this measures SPECTRAL_ONLY,
not FULL_PIPELINE. Measurement domain = SPECTRAL_ONLY.
"""
from __future__ import annotations
import numpy as np
from ..types import AceCertificate, CertLevel

MEASUREMENT_DOMAIN = "SPECTRAL_ONLY"  # ADR-001 open question — answer committed here
MAX_ITER = 1000
TOL = 1e-8


def certify_l2(
    K: np.ndarray,
    *,
    tau: float = 1.0,
    delta: float = 0.05,
    max_iter: int = MAX_ITER,
    tol: float = TOL,
) -> AceCertificate:
    """
    K: the contraction operator matrix (n×n, real or complex).
    Uses power iteration to estimate ρ(K) = spectral radius.
    """
    if K.ndim != 2 or K.shape[0] != K.shape[1]:
        raise ValueError("K must be a square matrix")

    n = K.shape[0]
    v = np.random.default_rng(seed=42).standard_normal(n)
    v = v / (np.linalg.norm(v) + 1e-12)

    rho_prev = 0.0
    for _ in range(max_iter):
        Kv = K @ v
        rho = float(np.linalg.norm(Kv))
        v = Kv / (rho + 1e-12)
        if abs(rho - rho_prev) < tol:
            break
        rho_prev = rho

    lipschitz_upper = rho
    gap_lb = 1.0 - lipschitz_upper
    certified = lipschitz_upper < (1.0 - delta)

    return AceCertificate(
        level=CertLevel.L2_POWERITER,
        certified=certified,
        lipschitz_upper=lipschitz_upper,
        gap_lb=max(0.0, gap_lb),
        contraction_rate=lipschitz_upper,
        budget_used=lipschitz_upper,
        tau=tau,
        delta=delta,
        margin=gap_lb - delta,
        tail_bound=float("inf") if lipschitz_upper >= 1.0
                   else tau / max(1e-12, gap_lb),
        details={
            "measurement_domain": MEASUREMENT_DOMAIN,
            "matrix_shape": list(K.shape),
            "iterations": max_iter,
            "tol": tol,
        },
    )
```


### `src/pirtm/ace/witness.py`

```python
"""
AceWitness: production artifact consumed by ETP's Static Tail.
Every certified ACE call emits exactly one witness, which the ETP Governor
uses as the contractionCertificate field in a PETCTraceAtom.
"""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass
from .types import AceCertificate


@dataclass(frozen=True)
class AceWitness:
    witness_id:    str    # SHA-256 of canonical JSON
    timestamp_iso: str
    cert:          AceCertificate
    prime_index:   int    # p ∈ P_N — filled by caller from PETC context

    @classmethod
    def from_certificate(
        cls,
        cert: AceCertificate,
        prime_index: int,
    ) -> "AceWitness":
        payload = {
            "level": cert.level.value,
            "certified": cert.certified,
            "lipschitz_upper": cert.lipschitz_upper,
            "gap_lb": cert.gap_lb,
            "tau": cert.tau,
            "delta": cert.delta,
            "prime_index": prime_index,
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        witness_id = hashlib.sha256(canonical.encode()).hexdigest()
        return cls(
            witness_id=witness_id,
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            cert=cert,
            prime_index=prime_index,
        )

    def is_valid_for_etp(self) -> bool:
        """ETP gate check: cert must be certified AND gap_lb > 0."""
        return self.cert.certified and self.cert.gap_lb > 0
```


### `src/pirtm/ace/protocol.py`

```python
"""
AceProtocol: single entry-point that dispatches to the correct level
based on available inputs, then emits an AceWitness for ETP.
"""
from __future__ import annotations
from typing import Sequence
import numpy as np
from pirtm.types import StepInfo
from .budget import AceBudget
from .witness import AceWitness
from .types import AceCertificate, CertLevel, AceBudgetState
from .levels.l0_heuristic import certify_l0
from .levels.l1_normbound import certify_l1
from .levels.l2_poweriter import certify_l2


class AceProtocol:
    """
    Stateful ACE protocol runner. Maintains a budget across calls.
    Caller must provide the prime_index from the active PETC chain.
    """

    def __init__(self, tau: float = 1.0, delta: float = 0.05) -> None:
        self.budget = AceBudget(tau=tau)
        self.delta = delta

    def certify_from_telemetry(
        self,
        records: Sequence[StepInfo],
        prime_index: int,
        *,
        tail_norm: float = 0.0,
    ) -> AceWitness:
        """L0 path — telemetry only."""
        cert = certify_l0(records, tau=self.budget.snapshot().tau,
                          tail_norm=tail_norm, delta=self.delta)
        self.budget.consume(cert.budget_used)
        return AceWitness.from_certificate(cert, prime_index)

    def certify_from_weights(
        self,
        weights: Sequence[float],
        basis_norms: Sequence[float],
        prime_index: int,
    ) -> AceWitness:
        """L1 path — weighted-ℓ₁ norm bound."""
        cert = certify_l1(weights, basis_norms,
                          tau=self.budget.snapshot().tau, delta=self.delta)
        self.budget.consume(cert.budget_used)
        return AceWitness.from_certificate(cert, prime_index)

    def certify_from_matrix(
        self,
        K: np.ndarray,
        prime_index: int,
    ) -> AceWitness:
        """L2 path — power iteration spectral radius."""
        cert = certify_l2(K, tau=self.budget.snapshot().tau, delta=self.delta)
        self.budget.consume(cert.budget_used)
        return AceWitness.from_certificate(cert, prime_index)

    def budget_state(self) -> AceBudgetState:
        return self.budget.snapshot()
```


***

## PETC Sub-Package — Expansions

### `src/pirtm/petc/signature.py`

```python
"""
PETC prime-exponent vector signatures.
A tensor's type identity is encoded as a vector of prime exponents:
  T of type p₂² · p₃¹ ↔ signature [2, 1, 0, ...]
Tensor product = signature addition (prime exponent addition).
Contraction on index i = decrement exponent at position i.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence


FIRST_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


@dataclass(frozen=True)
class PETCSignature:
    exponents: tuple[int, ...]  # exponent for each prime slot

    @classmethod
    def from_sequence(cls, exps: Sequence[int]) -> "PETCSignature":
        return cls(exponents=tuple(exps))

    @classmethod
    def zero(cls, n_slots: int = 15) -> "PETCSignature":
        return cls(exponents=(0,) * n_slots)

    def product(self, other: "PETCSignature") -> "PETCSignature":
        """Tensor product ↔ component-wise addition of exponents."""
        if len(self.exponents) != len(other.exponents):
            raise ValueError("Signature slot mismatch — cannot compute product")
        return PETCSignature(
            exponents=tuple(a + b for a, b in zip(self.exponents, other.exponents))
        )

    def contract(self, slot: int) -> "PETCSignature":
        """Contraction on prime slot — decrement exponent at position slot."""
        if slot < 0 or slot >= len(self.exponents):
            raise IndexError(f"slot {slot} out of range")
        if self.exponents[slot] <= 0:
            raise ValueError(
                f"PETC_SIGNATURE_CONTRACTION_UNDERFLOW: "
                f"slot {slot} already at 0"
            )
        exps = list(self.exponents)
        exps[slot] -= 1
        return PETCSignature(exponents=tuple(exps))

    def verify_matches(self, other: "PETCSignature") -> bool:
        return self.exponents == other.exponents

    def to_prime_product(self) -> int:
        """Decode back to integer: Π pᵢ^eᵢ."""
        result = 1
        for prime, exp in zip(FIRST_PRIMES, self.exponents):
            result *= prime ** exp
        return result
```


### `src/pirtm/petc/chain.py`

```python
"""
PETC chain with SHA-256 atomId and prevHash linking.
Provides the Merkle-ready chain that ETP's Jubilee checkpoint seals.
"""
from __future__ import annotations
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PETCAtom:
    atom_id:    str        # SHA-256 of canonical JSON
    prev_hash:  str        # previous atom's atom_id (or '0x0' for genesis)
    prime:      int
    timestamp:  str        # ISO-8601
    payload:    dict[str, Any]
    outcome:    str        # 'AUTHORIZED' | 'DENIED'


def _canonical_json(d: dict[str, Any]) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"))


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


class PETCChain:
    """
    Append-only, hash-linked chain of PETCAtoms.
    Each atom's atom_id commits to its content AND its predecessor.
    Chain integrity = every atom.prev_hash == chain[i-1].atom_id
    """

    def __init__(self) -> None:
        self._atoms: list[PETCAtom] = []

    def append(
        self,
        prime: int,
        payload: dict[str, Any],
        outcome: str = "AUTHORIZED",
    ) -> PETCAtom:
        prev_hash = self._atoms[-1].atom_id if self._atoms else "0x0"
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        raw = _canonical_json({
            "prev_hash": prev_hash,
            "prime": prime,
            "timestamp": ts,
            "payload": payload,
            "outcome": outcome,
        })
        atom_id = _sha256(raw)
        atom = PETCAtom(
            atom_id=atom_id,
            prev_hash=prev_hash,
            prime=prime,
            timestamp=ts,
            payload=payload,
            outcome=outcome,
        )
        self._atoms.append(atom)
        return atom

    def verify_integrity(self) -> tuple[bool, list[int]]:
        """Returns (is_valid, list_of_broken_link_indices)."""
        broken: list[int] = []
        for i in range(1, len(self._atoms)):
            if self._atoms[i].prev_hash != self._atoms[i - 1].atom_id:
                broken.append(i)
        return (len(broken) == 0, broken)

    def atoms(self) -> list[PETCAtom]:
        return list(self._atoms)

    def __len__(self) -> int:
        return len(self._atoms)
```


### `src/pirtm/petc/merkle.py`

```python
"""
Jubilee Merkle root builder.
Seals all PETCAtoms since the last Jubilee into a single Merkle root,
satisfying ETP's EpochJubilee.merkleRoot requirement.
"""
from __future__ import annotations
import hashlib
from .chain import PETCAtom


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _merkle_pair(a: str, b: str) -> str:
    return _sha256(a + b)


def build_merkle_root(atoms: list[PETCAtom]) -> str:
    """
    Builds a Merkle root from the atom_id list.
    Empty list → returns SHA-256 of empty string (sentinel).
    Single atom → returns its atom_id directly.
    """
    if not atoms:
        return _sha256("")
    leaves = [atom.atom_id for atom in atoms]
    while len(leaves) > 1:
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])  # duplicate last for odd-length layer
        leaves = [_merkle_pair(leaves[i], leaves[i + 1])
                  for i in range(0, len(leaves), 2)]
    return leaves[0]


def verify_merkle_inclusion(
    atom_id: str,
    proof: list[tuple[str, str]],  # (sibling_hash, position: 'L'|'R')
    root: str,
) -> bool:
    """Verify a Merkle inclusion proof for a single atom_id."""
    current = atom_id
    for sibling, position in proof:
        if position == "L":
            current = _merkle_pair(sibling, current)
        else:
            current = _merkle_pair(current, sibling)
    return current == root
```


***

## Test Harnesses — Full Suite

### `tests/test_ace_protocol.py`

```python
"""
ACE Protocol — full multi-level harness.
Covers: L0, L1, L2, budget guard, witness production.
Target: 90% line coverage on ace/ sub-package.
"""
import pytest
import numpy as np
from pirtm.types import StepInfo
from pirtm.ace.protocol import AceProtocol
from pirtm.ace.levels.l0_heuristic import certify_l0
from pirtm.ace.levels.l1_normbound import certify_l1
from pirtm.ace.levels.l2_poweriter import certify_l2
from pirtm.ace.types import CertLevel
from pirtm.ace.budget import AceBudget, MAX_DEPLETION_RATE


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def good_records():
    return [StepInfo(q=0.7, epsilon=0.1), StepInfo(q=0.8, epsilon=0.1)]

@pytest.fixture
def bad_records():
    return [StepInfo(q=1.1, epsilon=0.1)]   # q ≥ 1 → not contractive

@pytest.fixture
def contraction_matrix():
    # ‖K‖₂ = 0.5 — clearly contractive
    return np.array([[0.3, 0.1], [0.1, 0.4]])

@pytest.fixture
def non_contraction_matrix():
    # ‖K‖₂ > 1
    return np.array([[2.0, 0.5], [0.5, 1.5]])

@pytest.fixture
def protocol():
    return AceProtocol(tau=1.0, delta=0.05)


# ── L0 Tests ──────────────────────────────────────────────────────────────────

class TestL0Heuristic:
    def test_certified_on_contractive_records(self, good_records):
        cert = certify_l0(good_records)
        assert cert.level == CertLevel.L0_HEURISTIC
        assert cert.certified is True
        assert 0 < cert.lipschitz_upper < 1

    def test_not_certified_when_q_exceeds_threshold(self, bad_records):
        cert = certify_l0(bad_records)
        assert cert.certified is False

    def test_gap_lb_equals_one_minus_lipschitz(self, good_records):
        cert = certify_l0(good_records)
        assert abs(cert.gap_lb - (1.0 - cert.lipschitz_upper)) < 1e-9

    def test_raises_on_empty_records(self):
        with pytest.raises(ValueError, match="no telemetry"):
            certify_l0([])

    def test_tail_bound_infinite_when_q_ge_1(self, bad_records):
        cert = certify_l0(bad_records)
        assert cert.tail_bound == float("inf")

    def test_trl_level_is_2(self, good_records):
        cert = certify_l0(good_records)
        assert cert.level.trl == 2


# ── L1 Tests ──────────────────────────────────────────────────────────────────

class TestL1Normbound:
    def test_certified_on_contractive_weights(self):
        weights = [0.2, 0.3, 0.1]
        norms   = [1.0, 1.0, 1.0]
        cert = certify_l1(weights, norms)
        # ‖K‖ ≤ 0.6 < 0.95 → certified
        assert cert.certified is True
        assert abs(cert.lipschitz_upper - 0.6) < 1e-9

    def test_not_certified_when_norm_exceeds_threshold(self):
        weights = [0.5, 0.6]
        norms   = [1.0, 1.0]
        cert = certify_l1(weights, norms, delta=0.05)
        # ‖K‖ = 1.1 ≥ 1 − 0.05 = 0.95 → not certified
        assert cert.certified is False

    def test_raises_on_length_mismatch(self):
        with pytest.raises(ValueError, match="equal length"):
            certify_l1([0.1, 0.2], [1.0])

    def test_raises_on_empty_inputs(self):
        with pytest.raises(ValueError, match="empty"):
            certify_l1([], [])

    def test_budget_used_equals_lipschitz(self):
        weights = [0.3, 0.2]
        norms   = [1.0, 1.0]
        cert = certify_l1(weights, norms)
        assert abs(cert.budget_used - cert.lipschitz_upper) < 1e-9


# ── L2 Tests ──────────────────────────────────────────────────────────────────

class TestL2PowerIter:
    def test_certified_on_contractive_matrix(self, contraction_matrix):
        cert = certify_l2(contraction_matrix)
        assert cert.level == CertLevel.L2_POWERITER
        assert cert.certified is True
        assert cert.lipschitz_upper < 1.0

    def test_not_certified_on_expanding_matrix(self, non_contraction_matrix):
        cert = certify_l2(non_contraction_matrix)
        assert cert.certified is False
        assert cert.lipschitz_upper >= 1.0

    def test_spectral_radius_tighter_than_l1(self):
        # L2 should give a tighter (lower) ‖K‖ than L1 for same operator
        weights = [0.3, 0.3]
        norms   = [1.0, 1.0]
        K = np.diag([0.3, 0.3])
        l1_cert = certify_l1(weights, norms)
        l2_cert = certify_l2(K)
        assert l2_cert.lipschitz_upper <= l1_cert.lipschitz_upper + 1e-9

    def test_raises_on_non_square_matrix(self):
        with pytest.raises(ValueError, match="square"):
            certify_l2(np.array([[1, 2, 3]]))

    def test_measurement_domain_is_spectral_only(self, contraction_matrix):
        from pirtm.ace.levels.l2_poweriter import MEASUREMENT_DOMAIN
        assert MEASUREMENT_DOMAIN == "SPECTRAL_ONLY"

    def test_trl_level_is_3(self, contraction_matrix):
        cert = certify_l2(contraction_matrix)
        assert cert.level.trl == 3


# ── Budget Tests ──────────────────────────────────────────────────────────────

class TestAceBudget:
    def test_normal_consumption_succeeds(self):
        budget = AceBudget(tau=1.0)
        state = budget.consume(0.001)
        assert state.consumed == pytest.approx(0.001)

    def test_raises_on_depletion_rate_exceeded(self):
        budget = AceBudget(tau=1.0)
        with pytest.raises(RuntimeError, match="DEPLETION_RATE_EXCEEDED"):
            budget.consume(MAX_DEPLETION_RATE * 1.0 + 0.001)

    def test_raises_on_full_depletion(self):
        budget = AceBudget(tau=0.01)
        with pytest.raises(RuntimeError):
            budget.consume(0.009)  # first — ok
            budget.consume(0.002)  # depletes τ

    def test_raises_on_negative_amount(self):
        budget = AceBudget(tau=1.0)
        with pytest.raises(ValueError, match="≥ 0"):
            budget.consume(-0.001)

    def test_remaining_decreases_with_consumption(self):
        budget = AceBudget(tau=1.0)
        budget.consume(0.001)
        assert budget.snapshot().remaining < 1.0


# ── AceProtocol Integration ───────────────────────────────────────────────────

class TestAceProtocol:
    def test_certify_from_telemetry_emits_witness(self, protocol, good_records):
        witness = protocol.certify_from_telemetry(good_records, prime_index=7)
        assert witness.prime_index == 7
        assert len(witness.witness_id) == 64
        assert witness.is_valid_for_etp()

    def test_certify_from_weights_emits_witness(self, protocol):
        witness = protocol.certify_from_weights([0.2, 0.1], [1.0, 1.0], prime_index=11)
        assert witness.cert.level == CertLevel.L1_NORMBOUND
        assert witness.is_valid_for_etp()

    def test_certify_from_matrix_emits_witness(self, protocol, contraction_matrix):
        witness = protocol.certify_from_matrix(contraction_matrix, prime_index=13)
        assert witness.cert.level == CertLevel.L2_POWERITER
        assert witness.is_valid_for_etp()

    def test_witness_invalid_for_etp_on_non_contraction(self, protocol, bad_records):
        witness = protocol.certify_from_telemetry(bad_records, prime_index=5)
        assert witness.is_valid_for_etp() is False

    def test_budget_consumed_across_calls(self, good_records, contraction_matrix):
        proto = AceProtocol(tau=1.0)
        proto.certify_from_telemetry(good_records, prime_index=2)
        state = proto.budget_state()
        assert state.consumed > 0
```


### `tests/test_petc_signature.py`

```python
"""
PETC Signature — prime-exponent vector arithmetic.
"""
import pytest
from pirtm.petc.signature import PETCSignature


class TestPETCSignature:
    def test_product_adds_exponents(self):
        A = PETCSignature.from_sequence([2, 3, 0])
        B = PETCSignature.from_sequence([1, 0, 5])
        C = A.product(B)
        assert C.exponents == (3, 3, 5)

    def test_contract_decrements_slot(self):
        sig = PETCSignature.from_sequence([2, 1, 0])
        contracted = sig.contract(0)
        assert contracted.exponents == (1, 1, 0)

    def test_contract_underflow_raises(self):
        sig = PETCSignature.from_sequence([0, 1, 0])
        with pytest.raises(ValueError, match="UNDERFLOW"):
            sig.contract(0)

    def test_product_slot_mismatch_raises(self):
        A = PETCSignature.from_sequence([1, 2])
        B = PETCSignature.from_sequence([1, 2, 3])
        with pytest.raises(ValueError, match="mismatch"):
            A.product(B)

    def test_zero_signature_identity_under_product(self):
        A = PETCSignature.from_sequence([2, 3, 1])
        Z = PETCSignature.zero(3)
        assert A.product(Z).exponents == A.exponents

    def test_prime_product_decodes_correctly(self):
        # p₂^2 · p₃^1 = 4 · 3 = 12
        sig = PETCSignature.from_sequence([2, 1] + [0] * 13)
        assert sig.to_prime_product() == 12

    def test_verify_matches_self(self):
        sig = PETCSignature.from_sequence([1, 2, 3])
        assert sig.verify_matches(PETCSignature.from_sequence([1, 2, 3]))

    def test_verify_fails_on_mismatch(self):
        A = PETCSignature.from_sequence([1, 2, 3])
        B = PETCSignature.from_sequence([1, 2, 4])
        assert not A.verify_matches(B)
```


### `tests/test_petc_chain.py`

```python
"""
PETC Chain — prevHash-linked integrity.
"""
import pytest
from pirtm.petc.chain import PETCChain


class TestPETCChain:
    def test_genesis_atom_prev_hash_is_sentinel(self):
        chain = PETCChain()
        atom = chain.append(prime=2, payload={"step": 0})
        assert atom.prev_hash == "0x0"

    def test_second_atom_prev_hash_matches_first_atom_id(self):
        chain = PETCChain()
        a1 = chain.append(prime=2, payload={"step": 0})
        a2 = chain.append(prime=3, payload={"step": 1})
        assert a2.prev_hash == a1.atom_id

    def test_verify_integrity_passes_on_untampered_chain(self):
        chain = PETCChain()
        for p in [2, 3, 5, 7, 11]:
            chain.append(prime=p, payload={})
        valid, broken = chain.verify_integrity()
        assert valid is True
        assert broken == []

    def test_verify_integrity_catches_tampered_link(self):
        chain = PETCChain()
        chain.append(prime=2, payload={})
        chain.append(prime=3, payload={})
        # tamper
        chain._atoms[1] = chain._atoms[1].__class__(
            atom_id=chain._atoms[1].atom_id,
            prev_hash="TAMPERED",
            prime=chain._atoms[1].prime,
            timestamp=chain._atoms[1].timestamp,
            payload=chain._atoms[1].payload,
            outcome=chain._atoms[1].outcome,
        )
        valid, broken = chain.verify_integrity()
        assert valid is False
        assert 1 in broken

    def test_atom_id_is_64_hex_chars(self):
        chain = PETCChain()
        atom = chain.append(prime=5, payload={"test": True})
        assert len(atom.atom_id) == 64
        assert all(c in "0123456789abcdef" for c in atom.atom_id)

    def test_empty_chain_integrity_trivially_valid(self):
        chain = PETCChain()
        valid, broken = chain.verify_integrity()
        assert valid is True
        assert broken == []
```


### `tests/test_petc_merkle.py`

```python
"""
PETC Merkle — Jubilee root construction and inclusion proofs.
"""
import pytest
from pirtm.petc.chain import PETCChain
from pirtm.petc.merkle import build_merkle_root


class TestMerkleRoot:
    def test_empty_list_returns_sentinel(self):
        root = build_merkle_root([])
        assert len(root) == 64

    def test_single_atom_root_equals_atom_id(self):
        chain = PETCChain()
        atom = chain.append(prime=2, payload={})
        root = build_merkle_root([atom])
        assert root == atom.atom_id

    def test_two_atom_root_is_deterministic(self):
        chain = PETCChain()
        a1 = chain.append(prime=2, payload={})
        a2 = chain.append(prime=3, payload={})
        r1 = build_merkle_root([a1, a2])
        r2 = build_merkle_root([a1, a2])
        assert r1 == r2

    def test_root_changes_with_different_atoms(self):
        c1 = PETCChain()
        c1.append(prime=2, payload={"v": 1})
        c2 = PETCChain()
        c2.append(prime=2, payload={"v": 2})
        r1 = build_merkle_root(c1.atoms())
        r2 = build_merkle_root(c2.atoms())
        assert r1 != r2

    def test_odd_leaf_count_handled(self):
        chain = PETCChain()
        for p in [2, 3, 5]:
            chain.append(prime=p, payload={})
        root = build_merkle_root(chain.atoms())
        assert len(root) == 64

    def test_root_is_64_hex_chars(self):
        chain = PETCChain()
        for p in [2, 3, 5, 7]:
            chain.append(prime=p, payload={})
        root = build_merkle_root(chain.atoms())
        assert len(root) == 64
```


### `tests/test_ace_petc_coupling.py`

```python
"""
ACE ↔ PETC coupling integration test.
Validates: ACE certification emits a witness → witness binds to PETC atom
→ chain + Merkle root seals to ETP Jubilee checkpoint.
"""
import pytest
import numpy as np
from pirtm.types import StepInfo
from pirtm.ace.protocol import AceProtocol
from pirtm.ace.witness import AceWitness
from pirtm.petc.chain import PETCChain
from pirtm.petc.merkle import build_merkle_root


@pytest.fixture
def contractive_records():
    return [StepInfo(q=0.75, epsilon=0.1), StepInfo(q=0.80, epsilon=0.1)]

@pytest.fixture
def contractive_K():
    return np.diag([0.5, 0.4])


class TestAcePetcCoupling:
    def test_authorized_ace_produces_valid_petc_atom(
        self, contractive_records
    ):
        protocol = AceProtocol(tau=1.0)
        chain = PETCChain()

        witness = protocol.certify_from_telemetry(contractive_records, prime_index=7)
        assert witness.is_valid_for_etp()

        atom = chain.append(
            prime=witness.prime_index,
            payload={"witness_id": witness.witness_id,
                     "lipschitz_upper": witness.cert.lipschitz_upper},
            outcome="AUTHORIZED",
        )
        assert atom.prime == 7
        assert atom.payload["witness_id"] == witness.witness_id

    def test_l2_witness_binds_to_chain_and_merkle(self, contractive_K):
        protocol = AceProtocol(tau=1.0)
        chain = PETCChain()

        for prime_idx in [2, 3, 5]:
            witness = protocol.certify_from_matrix(contractive_K, prime_index=prime_idx)
            chain.append(
                prime=prime_idx,
                payload={"witness_id": witness.witness_id},
                outcome="AUTHORIZED" if witness.is_valid_for_etp() else "DENIED",
            )

        valid, broken = chain.verify_integrity()
        assert valid is True

        root = build_merkle_root(chain.atoms())
        assert len(root) == 64

    def test_denied_ace_emits_denied_petc_atom(self):
        protocol = AceProtocol(tau=1.0)
        chain = PETCChain()
        bad_records = [StepInfo(q=1.1, epsilon=0.1)]

        witness = protocol.certify_from_telemetry(bad_records, prime_index=5)
        assert not witness.is_valid_for_etp()

        atom = chain.append(
            prime=5,
            payload={"witness_id": witness.witness_id},
            outcome="DENIED",
        )
        assert atom.outcome == "DENIED"

    def test_jubilee_triggers_at_zero_data_debt(self, contractive_records):
        """Simulates ETP L(t)=0: full ACE→PETC→Merkle seal cycle."""
        protocol = AceProtocol(tau=1.0)
        chain = PETCChain()

        for prime_idx, rec in zip([2, 3, 5], [contractive_records] * 3):
            witness = protocol.certify_from_telemetry(rec, prime_index=prime_idx)
            chain.append(prime=prime_idx,
                         payload={"witness_id": witness.witness_id},
                         outcome="AUTHORIZED")

        # Simulate L(t)=0 → Jubilee
        root = build_merkle_root(chain.atoms())
        assert root is not None
        assert len(chain) == 3
```


***

## CI Workflow — `ace-petc-checks.yml`

```yaml
name: ACE Protocol + PETC Module Checks
on:
  push:
    branches: [main]
  pull_request:
    paths:
      - 'src/pirtm/ace/**'
      - 'src/pirtm/petc/**'
      - 'src/pirtm/certify.py'
      - 'src/pirtm/petc.py'
      - 'tests/test_ace_*.py'
      - 'tests/test_petc_*.py'

jobs:
  ace-petc-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - name: Run ACE + PETC unit tests
        run: |
          pytest tests/test_ace_protocol.py \
                 tests/test_ace_budget.py \
                 tests/test_ace_witness.py \
                 tests/test_petc_signature.py \
                 tests/test_petc_chain.py \
                 tests/test_petc_merkle.py \
                 tests/test_ace_petc_coupling.py \
                 --cov=src/pirtm/ace \
                 --cov=src/pirtm/petc \
                 --cov-fail-under=90 \
                 -v
      - name: Regression: existing test_petc.py still passes
        run: pytest tests/test_petc.py tests/test_certify.py -v
      - name: TRL annotation check
        run: |
          python -c "
          from pirtm.ace.types import CertLevel
          for lvl in CertLevel:
              assert lvl.trl in (2,3,4), f'Missing TRL for {lvl}'
          print('All CertLevel entries have valid TRL annotations.')
          "
```


***

## Precision Question (ACE/PETC Gate)

> `certify.py`'s public `ace_certificate()` currently returns a `Certificate` (from `pirtm.types`) while the new `ace/` sub-package returns an `AceCertificate`.  Before `certify.py` is refactored to re-export from `ace/`, the question is: **should `ace_certificate()` be a backwards-compatible alias that returns the legacy `Certificate` dataclass, or should it be promoted to return `AceCertificate` with a migration guide for callers?** This choice gates whether `petc_bridge.py` and any downstream consumers in Q-Calculator's `packages/guardian` can adopt the new type without a breaking change.

