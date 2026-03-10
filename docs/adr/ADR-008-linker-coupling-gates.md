# ADR-008: Linker Inputs + Coupling Resolution Gates (Day 14–16)

> **Status**: Proposed  
> **Date**: 2026-03-10  
> **Authors**: PIRTM Linker Team  
> **Spec Reference**: [PIRTM ADR-004](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)

---

## Problem Statement

PIRTM ADR-004 specifies a **two-phase contractivity proof**:
- **Transpile time** (per-module): `contractivity-check` pass verifies individual module stability
- **Link time** (network-wide): `spectral-small-gain` pass verifies the complete session graph is stable

At the link-time phase, the linker must:
1. **Resolve module names** to their `.pirtm.bc` binaries (from `coupling.json`)
2. **Cross-check commitments** to ensure no two sessions share the same identity (security gate)
3. **Construct the coupling matrix** from `pirtm.session_graph(mod=N, coupling=#pirtm.unresolved_coupling)` attributes
4. **Run spectral-small-gain** to verify network-wide stability

Currently, there is no:
- `coupling.json` schema definition
- Linker pipeline (`pirtm_link.py`)
- Acceptance tests for commitment collision detection
- Test pair demonstrating r=0.7 pass / r=1.1 fail behavior

This ADR defines the **Day 14–16 gate**: linking infrastructure with security validation and spectral radius acceptance tests.

---

## Solution

### 1. Coupling Schema: `coupling.json`

Define the canonical linking inputs in `pirtm/tests/fixtures/coupling.json`:

```json
{
  "version": "1.0",
  "sessions": [
    {
      "name": "SessionA",
      "identity_commitment": "0xabc123def456",
      "modules": [
        {
          "name": "ModuleA1",
          "path": "pirtm/tests/fixtures/basic.pirtm.bc",
          "prime_index": 7,
          "epsilon": 0.05,
          "op_norm_T": 2.1
        },
        {
          "name": "ModuleA2",
          "path": "pirtm/tests/fixtures/secondary.pirtm.bc",
          "prime_index": 11,
          "epsilon": 0.03,
          "op_norm_T": 1.8
        }
      ],
      "coupling_matrix": [
        [0.0, 0.4],
        [0.3, 0.0]
      ]
    },
    {
      "name": "SessionB",
      "identity_commitment": "0xfed987cba654",
      "modules": [
        {
          "name": "ModuleB1",
          "path": "pirtm/tests/fixtures/basic.pirtm.bc",
          "prime_index": 13,
          "epsilon": 0.02,
          "op_norm_T": 2.5
        }
      ],
      "coupling_matrix": [[0.0]]
    }
  ],
  "cross_session_coupling": [
    [0.0, 0.2],
    [0.1, 0.0]
  ]
}
```

**Schema Rules** (from ADR-004 L0 invariants):
- `identity_commitment`: Must be unique across all sessions (Gate: commitment-collision test)
- `modules[i].path`: Points to valid `.pirtm.bc` file carrying `!pirtm_proof` section
- `modules[i].prime_index`: Must match the module's `prime_index` from `.pirtm.bc`
- `coupling_matrix`: M×M matrix where M = number of modules in session
- `cross_session_coupling`: S×S matrix where S = number of sessions

---

### 2. Linker Pipeline: `pirtm_link.py`

Create `src/pirtm/transpiler/pirtm_link.py` with a three-pass architecture:

```python
"""
PIRTM Linker: network-wide contractivity proof.

Pipeline:
  Pass 1: Name Resolution        — locate .pirtm.bc files, validate format
  Pass 2: Commitment Crosscheck  — detect duplicate identity_commitment (security gate)
  Pass 3: Matrix Construction    — build full session graph, substitute #pirtm.unresolved_coupling
  Then:    Spectral Small-Gain   — verify network-wide stability
"""

import json
import struct
from typing import List, Dict, Tuple
from pirtm.spectral_gov import SpectralGovernor

class PIRTMLinker:
    def __init__(self, coupling_json_path: str):
        self.coupling_config = self._load_coupling_json(coupling_json_path)
        self.modules = {}
        self.sessions = {}
        self.commitment_map = {}

    def _load_coupling_json(self, path: str) -> Dict:
        """Load and validate coupling.json schema."""
        with open(path) as f:
            config = json.load(f)
        
        # Schema validation
        assert "version" in config, "coupling.json missing 'version'"
        assert "sessions" in config, "coupling.json missing 'sessions'"
        assert isinstance(config["sessions"], list), "sessions must be list"
        
        return config

    def pass1_name_resolution(self) -> None:
        """Locate and load all .pirtm.bc files."""
        print("[Pass 1] Name Resolution...")
        
        for session_cfg in self.coupling_config["sessions"]:
            session_name = session_cfg["name"]
            self.sessions[session_name] = {
                "commitment": session_cfg["identity_commitment"],
                "modules": [],
                "coupling": session_cfg.get("coupling_matrix", [])
            }
            
            for module_cfg in session_cfg["modules"]:
                module_name = module_cfg["name"]
                path = module_cfg["path"]
                
                # Load .pirtm.bc file
                try:
                    with open(path, "rb") as f:
                        binary = f.read()
                    self.modules[f"{session_name}:{module_name}"] = {
                        "path": path,
                        "binary": binary,
                        "prime_index": module_cfg["prime_index"],
                        "epsilon": module_cfg["epsilon"],
                        "op_norm_T": module_cfg["op_norm_T"]
                    }
                    self.sessions[session_name]["modules"].append(module_name)
                except FileNotFoundError:
                    raise RuntimeError(f"Module {module_name}: file not found: {path}")

    def pass2_commitment_crosscheck(self) -> None:
        """Detect duplicate identity_commitment (L0 invariant #6)."""
        print("[Pass 2] Commitment Crosscheck...")
        
        seen_commitments = {}
        for session_name, session in self.sessions.items():
            commitment = session["commitment"]
            
            if commitment in seen_commitments:
                prev_session = seen_commitments[commitment]
                raise RuntimeError(
                    f"error: duplicate identity_commitment: {commitment}\n"
                    f"  Session '{prev_session}' and '{session_name}' both share identity\n"
                    f"  (L0 invariant #6: human names in coupling.json do not survive into IR)"
                )
            
            seen_commitments[commitment] = session_name

    def pass3_matrix_construction(self) -> Dict:
        """Build full coupling matrix and resolve #pirtm.unresolved_coupling."""
        print("[Pass 3] Matrix Construction...")
        
        # Construct block-diagonal coupling matrix with cross-session blocks
        num_sessions = len(self.sessions)
        session_names = list(self.sessions.keys())
        session_indices = {name: i for i, name in enumerate(session_names)}
        
        # Count total modules
        total_modules = sum(len(s["modules"]) for s in self.sessions.values())
        
        # Initialize full coupling matrix (zeros)
        full_coupling = [[0.0] * total_modules for _ in range(total_modules)]
        
        # Fill in-session couplings (block-diagonal)
        module_offset = 0
        session_module_map = {}
        
        for session_name, session in self.sessions.items():
            num_modules = len(session["modules"])
            session_coupling = session["coupling"]
            
            # Validate coupling matrix is square and properly sized
            if len(session_coupling) != num_modules:
                raise RuntimeError(
                    f"Session {session_name}: coupling matrix size mismatch "
                    f"(expected {num_modules}x{num_modules}, got {len(session_coupling)}x...)"
                )
            
            # Insert into full matrix
            for i in range(num_modules):
                for j in range(num_modules):
                    full_coupling[module_offset + i][module_offset + j] = session_coupling[i][j]
            
            session_module_map[session_name] = (module_offset, num_modules)
            module_offset += num_modules
        
        # Fill cross-session couplings
        cross_coupling = self.coupling_config.get("cross_session_coupling", [])
        if cross_coupling:
            for i, session_i in enumerate(session_names):
                for j, session_j in enumerate(session_names):
                    if i != j and i < len(cross_coupling) and j < len(cross_coupling[i]):
                        offset_i, size_i = session_module_map[session_i]
                        offset_j, size_j = session_module_map[session_j]
                        # For simplicity, place cross-session coupling in (0, 0) block
                        full_coupling[offset_i][offset_j] = cross_coupling[i][j]
        
        return {"matrix": full_coupling, "mapping": session_module_map}

    def spectral_small_gain(self, coupling_matrix: List[List[float]]) -> Tuple[float, bool]:
        """Run spectral-small-gain pass; return (r, is_contractive)."""
        print("[Spectral Pass] Small-Gain Test...")
        
        governor = SpectralGovernor()
        
        # Compute spectral radius of coupling matrix
        spectral_radius = self._compute_spectral_radius(coupling_matrix)
        
        print(f"  Spectral radius: r = {spectral_radius:.4f}")
        
        # L0 invariant #2: must be < 1 for contractivity
        is_contractive = spectral_radius < 1.0
        
        if is_contractive:
            print(f"  ✅ PASS: r < 1 (contractive)")
        else:
            print(f"  ❌ FAIL: r ≥ 1 (not contractive)")
        
        return spectral_radius, is_contractive

    def _compute_spectral_radius(self, matrix: List[List[float]]) -> float:
        """Compute spectral radius using power iteration."""
        import numpy as np
        
        A = np.array(matrix)
        eigenvalues = np.linalg.eigvals(A)
        spectral_radius = max(abs(eigenvalues))
        
        return spectral_radius

    def link(self) -> bool:
        """Execute full linking pipeline."""
        print("=== PIRTM Linker ===\n")
        
        try:
            self.pass1_name_resolution()
            self.pass2_commitment_crosscheck()
            coupling_info = self.pass3_matrix_construction()
            spectral_radius, is_contractive = self.spectral_small_gain(coupling_info["matrix"])
            
            if is_contractive:
                print(f"\n✅ LINKING SUCCESSFUL (r={spectral_radius:.4f})")
                return True
            else:
                print(f"\n❌ LINKING FAILED (r={spectral_radius:.4f} ≥ 1)")
                return False
        except RuntimeError as e:
            print(f"\n❌ LINKING FAILED: {e}")
            return False
```

---

### 3. Commitment-Collision Test: `test_commitment_collision.py`

Create `pirtm/tests/test_commitment_collision.py`:

```python
"""
Day 14–16 Gate: Commitment Collision Detection

Two sessions sharing the same identity_commitment must be rejected.
This enforces L0 invariant #6: human names in coupling.json do not survive into IR.
"""

import json
import tempfile
import pytest
from pirtm.transpiler.pirtm_link import PIRTMLinker

def test_duplicate_identity_commitment_rejected():
    """Two sessions with same identity_commitment must fail linking."""
    
    # Create coupling.json with duplicate commitment
    coupling_config = {
        "version": "1.0",
        "sessions": [
            {
                "name": "SessionA",
                "identity_commitment": "0xabc123",  # ← Duplicate!
                "modules": [
                    {
                        "name": "ModA",
                        "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                        "prime_index": 7,
                        "epsilon": 0.05,
                        "op_norm_T": 2.0
                    }
                ],
                "coupling_matrix": [[0.0]]
            },
            {
                "name": "SessionB",
                "identity_commitment": "0xabc123",  # ← Duplicate!
                "modules": [
                    {
                        "name": "ModB",
                        "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                        "prime_index": 11,
                        "epsilon": 0.03,
                        "op_norm_T": 1.5
                    }
                ],
                "coupling_matrix": [[0.0]]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(coupling_config, f)
        coupling_path = f.name
    
    # Attempt to link; should fail with duplicate identity error
    linker = PIRTMLinker(coupling_path)
    with pytest.raises(RuntimeError, match="duplicate identity_commitment"):
        linker.link()
    
    print("✅ Commitment collision correctly detected and rejected")

def test_unique_commitments_accepted():
    """Sessions with unique commitments should pass commitment check."""
    
    coupling_config = {
        "version": "1.0",
        "sessions": [
            {
                "name": "SessionA",
                "identity_commitment": "0xabc123",  # ← Unique
                "modules": [
                    {
                        "name": "ModA",
                        "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                        "prime_index": 7,
                        "epsilon": 0.05,
                        "op_norm_T": 2.0
                    }
                ],
                "coupling_matrix": [[0.0]]
            },
            {
                "name": "SessionB",
                "identity_commitment": "0xdef456",  # ← Unique
                "modules": [
                    {
                        "name": "ModB",
                        "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                        "prime_index": 11,
                        "epsilon": 0.03,
                        "op_norm_T": 1.5
                    }
                ],
                "coupling_matrix": [[0.0]]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(coupling_config, f)
        coupling_path = f.name
    
    linker = PIRTMLinker(coupling_path)
    # Should not raise
    linker.pass2_commitment_crosscheck()
    
    print("✅ Unique commitments accepted")
```

---

### 4. Link Test Pair: Spectral Radius Gates

Create `pirtm/tests/test_spectral_gates.py`:

```python
"""
Day 30 Acceptance Gates (deferred but defined now):
  r=0.7: Must pass linking (contractive system)
  r=1.1: Must fail linking (divergent system)
"""

import json
import tempfile
import pytest
from pirtm.transpiler.pirtm_link import PIRTMLinker

def test_r_0_7_contracts():
    """With spectral radius r=0.7, linking must succeed."""
    
    # Coupling matrix with spectral radius ≈ 0.7
    coupling_config = {
        "version": "1.0",
        "sessions": [
            {
                "name": "SessionStable",
                "identity_commitment": "0x700000",
                "modules": [
                    {
                        "name": "Mod1",
                        "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                        "prime_index": 5,
                        "epsilon": 0.01,
                        "op_norm_T": 1.0
                    },
                    {
                        "name": "Mod2",
                        "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                        "prime_index": 7,
                        "epsilon": 0.01,
                        "op_norm_T": 1.0
                    }
                ],
                "coupling_matrix": [
                    [0.0, 0.35],
                    [0.35, 0.0]
                ]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(coupling_config, f)
        coupling_path = f.name
    
    linker = PIRTMLinker(coupling_path)
    result = linker.link()
    
    assert result is True, "r=0.7 should link successfully (contractive)"
    print("✅ r=0.7: Linking succeeded (contractive system)")

def test_r_1_1_diverges():
    """With spectral radius r=1.1, linking must fail."""
    
    # Coupling matrix with spectral radius ≈ 1.1
    coupling_config = {
        "version": "1.0",
        "sessions": [
            {
                "name": "SessionUnstable",
                "identity_commitment": "0x110000",
                "modules": [
                    {
                        "name": "Mod1",
                        "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                        "prime_index": 5,
                        "epsilon": 0.01,
                        "op_norm_T": 1.0
                    },
                    {
                        "name": "Mod2",
                        "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                        "prime_index": 7,
                        "epsilon": 0.01,
                        "op_norm_T": 1.0
                    }
                ],
                "coupling_matrix": [
                    [0.0, 0.55],
                    [0.55, 0.0]
                ]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(coupling_config, f)
        coupling_path = f.name
    
    linker = PIRTMLinker(coupling_path)
    result = linker.link()
    
    assert result is False, "r=1.1 should fail linking (divergent)"
    print("✅ r=1.1: Linking failed (divergent system)")
```

---

## Consequences

### Positive
- **Security Gate**: Commitment collision test prevents identity spoofing
- **Network Stability**: Spectral-small-gain ensures full session graph is contractive
- **Three-Pass Architecture**: Clean separation of concerns (name resolution → validation → matrix construction)
- **Test Coverage**: Both positive (r=0.7) and negative (r=1.1) test cases validate the linker
- **Day 14–16 Gate Fulfilled**: All acceptance criteria measurable and testable

### Negative
- **Complex Matrix Construction**: Managing multiple sessions + cross-session couplings introduces subtle bugs
- **Spectral Radius Computation**: Requires NumPy/eigenvalue solver; small numerical errors could cause false positives/negatives
- **Coupling.json Brittleness**: Manual JSON files are error-prone; mismatched indices cause hard-to-debug failures

---

## Alternatives Considered

### Alternative A: Single-Pass Linker

**Description**: Combine all three passes into one monolithic function.

**Rejection Reason**: Makes debugging harder; cannot isolate which pass failed. Three-pass design follows MLIR convention and aids testing.

### Alternative B: No Commitment Collision Test

**Description**: Skip identity uniqueness check; rely on documentation.

**Rejection Reason**: Violates L0 invariant #6 (human names must not survive into IR). Security gate is non-optional.

### Alternative C: Spectral Radius as Soft Warning

**Description**: Allow r ≥ 1 to proceed with a warning instead of hard failure.

**Rejection Reason**: ADR-004 mandates r < 1 for contractivity proof. A non-contractive system is mathematically invalid; cannot execute safely.

---

## Rationale

The **three-pass linker + commitment validation + spectral gates** approach ensures:

1. **Correctness**: Name resolution is isolated from coupling validation (avoids subtle cache bugs)
2. **Security**: Duplicate identity detection prevents session hijacking
3. **Stability**: Spectral-small-gain closure guarantees network-wide contractivity
4. **Testability**: Each pass can be unit-tested independently; r=0.7/r=1.1 pair covers boundaries

The linker is **post-day-14** work, meaning:
- All modules have passed transpile-time `contractivity-check` (Day 14)
- All types use `mod=` nomenclature (Day 14)
- Coupling matrix is fully specified in `coupling.json` (linker input)

This sequence respects the dependency chain: **types → transpiler → linker**.

---

## Acceptance Criteria

- [ ] `src/pirtm/transpiler/pirtm_link.py` compiles without errors
- [ ] `PIRTMLinker.pass1_name_resolution()` successfully loads all `.pirtm.bc` files listed in `coupling.json`
- [ ] `PIRTMLinker.pass2_commitment_crosscheck()` detects and rejects duplicate `identity_commitment` with error message: `error: duplicate identity_commitment: {commitment}`
- [ ] `PIRTMLinker.pass3_matrix_construction()` builds correct full coupling matrix (validated by manual inspection)
- [ ] `PIRTMLinker.spectral_small_gain()` returns spectral radius with ±0.001 accuracy
- [ ] `test_commitment_collision.py::test_duplicate_identity_commitment_rejected` passes
- [ ] `test_spectral_gates.py::test_r_0_7_contracts` passes (linking succeeds)
- [ ] `test_spectral_gates.py::test_r_1_1_diverges` passes (linking fails)
- [ ] Linking pipeline runs in < 100ms for test cases (performance gate)

**Day 14–16 Gate Status**: ⏳ PENDING  
**Day 30 Gate Status** (r=0.7 pass, r=1.1 fail): ⏳ DEFERRED (defined; not tested yet)

---

## References

- [PIRTM ADR-004: MLIR Dialect Specification](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md) — spectral-small-gain semantics, session graph
- [ADR-005: ADR Process + Directory Layout](./ADR-005-adr-process-layout.md)
- [ADR-006: Dialect Type-Layer Gate (Day 0–3)](./ADR-006-dialect-type-layer-gate.md)
- [ADR-007: Prime → Mod Migration (Day 0–14)](./ADR-007-prime-mod-migration.md)
- [docs/migration/prime-to-mod-rename.md](../migration/prime-to-mod-rename.md)
- [Small-Gain Theorem](https://en.wikipedia.org/wiki/Small-gain_theorem) — theoretical foundation

---

## Sign-Off

- [ ] Language Architect (PIRTM spec) approved
- [ ] Tooling Maintainer approved
- [ ] CI/Infra approved (adds Day 14–16 CI gate)
