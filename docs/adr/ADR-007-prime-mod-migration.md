# ADR-007: Prime → Mod Migration + Shim Protocol (Day 0–14)

> **Status**: Proposed  
> **Date**: 2026-03-10  
> **Authors**: PIRTM Migration Team  
> **Spec Reference**: [PIRTM ADR-004](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)

---

## Problem Statement

PIRTM ADR-004 establishes `mod=` as the canonical nomenclature for all type moduli:
- `!pirtm.cert(mod=p)`
- `!pirtm.epsilon(mod=p, value=ε)`
- `!pirtm.op_norm_t(mod=p, norm=n)`
- `pirtm.session_graph` with `prime_index` and `epsilon` fields

However, the existing codebase may have used older naming conventions (e.g., `prime_index`, `PrimeChannel.prime`). This creates two problems:

1. **Nomenclature Drift**: Code uses `prime` and `mod` interchangeably, confusing maintenance
2. **Non-Atomic Migration**: A single large rename across many files introduces merge conflicts and makes code review difficult

This ADR defines a **two-phase migration strategy**:
- **Phase 1 (Day 0–7)**: Introduce shim protocol; old code works via property mappers
- **Phase 2 (Day 7–14)**: Structured per-file migration; validation via grep gates
- **Phase 3 (Day 14)**: Final atomic rename; `pirtm inspect` verifies full compliance

---

## Solution

### 1. Shim Protocol: `PrimeChannel.prime → .mod` Mapping

Create a compatibility shim in `src/pirtm/channels/shim.py` that allows old code to continue working:

```python
# src/pirtm/channels/shim.py
"""
Backward compatibility shim for prime → mod nomenclature transition.

During migration (Day 0–14):
  - Old code uses: channel.prime, module.prime_index
  - Shim maps to: channel.mod, module.prime_index (stored as property)
  - Verifier sees: mod= in the MLIR dialect

After Day 14:
  - All code uses: mod, prime_index (unchanged field names)
  - Shimming layer is removed
"""

class PrimeChannelShim:
    """Wraps a channel to provide both .prime and .mod for compatibility."""
    
    def __init__(self, mod_value: int):
        self._mod = mod_value
    
    @property
    def prime(self) -> int:
        """Deprecated: use .mod instead."""
        return self._mod
    
    @property
    def mod(self) -> int:
        """Canonical MLIR-friendly modulus value."""
        return self._mod
    
    def __str__(self):
        return f"mod={self._mod}"


class SessionGraphShim:
    """Wraps SessionGraph to map old prime_index field to modern .mod context."""
    
    def __init__(self, prime_index: int, epsilon: float, op_norm_T: float):
        self.prime_index = prime_index  # L0 invariant #1: exactly one
        self.epsilon = epsilon
        self.op_norm_T = op_norm_T
        self._coupling = None
    
    @property
    def mod(self) -> int:
        """Alias for prime_index (for MLIR emission)."""
        return self.prime_index
    
    def set_coupling(self, coupling_matrix):
        """Link-time coupling assignment (L0 invariant #4)."""
        if hasattr(self, '_coupling') and self._coupling is not None:
            raise RuntimeError("coupling already resolved")
        self._coupling = coupling_matrix
    
    def __repr__(self):
        return f"SessionGraph(prime_index={self.prime_index}, ε={self.epsilon}, ‖T‖={self.op_norm_T})"
```

**Key Properties**:
- Old code reads `channel.prime`; shim returns `channel.mod`
- No breakage during migration window
- MLIR verifier always sees `mod=` (canonical form)
- Shim is temporary; removed after Day 14 once all code is migrated

### 2. Structured Migration Guide: `docs/migration/prime-to-mod-rename.md`

Create a **per-file audit table** showing which files need renaming and which do not:

```markdown
# Prime → Mod Migration Checklist (Day 0–14)

## Tier 1: MLIR Dialect Layer (Day 0–3, locked after ADR-006 acceptance)

| File | Renaming Status | Details |
| :--- | :--- | :--- |
| `pirtm/dialect/pirtm.td` | ✅ RENAMED (Day 0) | All types use `mod=` in TableGen; canonical form |
| `pirtm/dialect/pirtm_types.cpp` | ✅ RENAMED (Day 0) | Verifiers check `mod` parameter |

## Tier 2: Channel Layer (Day 0–3, shim active)

| File | Renaming Status | Details |
| :--- | :--- | :--- |
| `src/pirtm/channels/base.py` | ⚠️ SHIM (Day 0–7) | Provide both `.prime` and `.mod` properties |
| `src/pirtm/channels/pirtm_channel.py` | ⚠️ SHIM (Day 0–7) | Constructor uses internal `_mod`, properties expose both |

## Tier 3: Transpiler Layer (Day 3–7)

| File | Renaming Status | Grep Gate | Details |
| :--- | :--- | :--- | :--- |
| `src/pirtm/transpiler/mlir_emitter.py` | ⚠️ REFACTOR (Day 3–7) | `grep -E "(\.prime(?!\w)\|_prime)" mlir_emitter.py` should return 0 lines | Emit `mod=` in all MLIR output; stop using `.prime` internally |
| `src/pirtm/transpiler/parser.py` | ⚠️ REFACTOR (Day 3–7) | `grep -E "(\.prime(?!\w)\|_prime)" parser.py` should return 0 lines | Parse `mod=` from input; map to internal `.mod` attribute |

## Tier 4: Core Algorithm Layer (Day 7–14)

| File | Renaming Status | Grep Gate | Details |
| :--- | :--- | :--- | :--- |
| `src/pirtm/core/contractivity.py` | ⚠️ REFACTOR (Day 7–14) | `grep -E "(\.prime(?!\w)\|_prime)" contractivity.py` should return 0 lines | Use `.mod` for all calculations; remove `.prime` references |
| `src/pirtm/core/projection.py` | ⚠️ REFACTOR (Day 7–14) | `grep -E "(\.prime(?!\w)\|_prime)" projection.py` should return 0 lines | Use `.mod` for all projections |
| `src/pirtm/core/gain.py` | ⚠️ REFACTOR (Day 7–14) | `grep -E "(\.prime(?!\w)\|_prime)" gain.py` should return 0 lines | Use `.mod` for spectral radius computation |

## Tier 5: Linking Layer (Day 14–16, locked after Day 14)

| File | Renaming Status | Details |
| :--- | :--- | :--- |
| `src/pirtm/transpiler/pirtm_link.py` | ✅ RENAMED (Day 14) | All inputs now use `mod=`; no `.prime` references remain |

---

## Acceptance Criteria by Gate

### Day 0–3 Gate (ADR-006)
- ✅ `pirtm.td` compiles with all types using `mod=`
- ✅ `pirtm_types.cpp` verifier checks `.mod` parameter
- ✅ `mlir-opt --verify-diagnostics` passes on four basic test cases

### Day 3–7 Gate (This ADR)
- ✅ Shim layer in `PrimeChannelShim` compiles and provides both `.prime` and `.mod`
- ✅ `mlir_emitter.py` emits MLIR with `mod=` for all types
- ✅ Grep gate 1 passes: `grep -r "\.prime\b" pirtm/ | grep -v "__pycache__" | grep -v ".pyc"` returns 0 lines (no live `.prime` refs)

### Day 7–14 Gate (This ADR)
- ✅ All `examples/` round-trip via `mlir_emitter.py --output mlir` without error
- ✅ Grep gate 2 passes: `grep -r "_prime\b" pirtm/ | grep -v "__pycache__" | grep -v ".pyc"` returns 0 lines (no internal `_prime` attributes)

### Day 14 Gate (Final Atomic Rename)
- ✅ `pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"` shows all modules verified
- ✅ Shim layer removed entirely; no `.prime` or `_prime` in codebase
- ✅ `pirtm.session_graph` carries `prime_index` field (as per ADR-004 L0 #1)

---

## Grep Gate Commands

Run these commands at the specified gates to validate migration progress:

### Gate 1 (Day 3–7): No `.prime` property access in transpiler

```bash
#!/bin/bash
# Check that transpiler layer has no .prime property access
# Expected: 0 lines returned (migration complete for transpiler)

if grep -r "\.prime\b" pirtm/ --include="*.py" \
    | grep -v "__pycache__" \
    | grep -v ".pyc" \
    | grep -v "# COMPAT:" \
    | wc -l | grep -q "^0$"; then
  echo "✅ GATE 1 PASS: No .prime properties remain in active code"
  exit 0
else
  echo "❌ GATE 1 FAIL: Found .prime properties. Must migrate:"
  grep -r "\.prime\b" pirtm/ --include="*.py" | grep -v "__pycache__"
  exit 1
fi
```

### Gate 2 (Day 7–14): No `_prime` internal attributes in core layer

```bash
#!/bin/bash
# Check that core layer has no _prime internal attributes
# Expected: 0 lines returned (migration complete for core)

if grep -r "_prime\b" pirtm/ --include="*.py" \
    | grep -v "__pycache__" \
    | grep -v ".pyc" \
    | grep -v "# COMPAT:" \
    | wc -l | grep -q "^0$"; then
  echo "✅ GATE 2 PASS: No _prime attributes remain in active code"
  exit 0
else
  echo "❌ GATE 2 FAIL: Found _prime attributes. Must migrate:"
  grep -r "_prime\b" pirtm/ --include="*.py" | grep -v "__pycache__"
  exit 1
fi
```

### Day 14 Final: Full atomic merge

```bash
#!/bin/bash
# Gate 3: Verify complete atomic merge
# Expected: All files migrated, shim removed, tests pass

set -e

echo "Checking for residual .prime or _prime..."
grep -r "\.prime\b\|_prime\b" pirtm/ --include="*.py" \
    | grep -v "__pycache__" \
    | grep -v ".pyc" && \
  { echo "❌ FAIL: Found residual naming"; exit 1; } || true

echo "Verifying pirtm inspect output..."
pirtm inspect basic.pirtm.bc | grep -q "contractivity_check: PASS" || \
  { echo "❌ FAIL: contractivity check not passing"; exit 1; }

echo "✅ GATE 3 PASS: Full atomic merge complete"
exit 0
```

---

### 3. Acceptance Tests: Round-Trip via `mlir_emitter.py`

Create test suite `pirtm/tests/test_roundtrip.py`:

```python
"""
Day 7–14 acceptance tests: round-trip MLIR via mlir_emitter.py

Each test in pirtm/examples/ must:
  1. Parse via mlir_emitter
  2. Emit valid MLIR with mod= for all types
  3. Pass --verify-diagnostics
  4. Preserve semantics (contractivity proof, coupling structure)
"""

import subprocess
import os

def test_roundtrip_examples():
    """All .pirtm files in examples/ should round-trip cleanly."""
    examples_dir = "pirtm/examples"
    
    for filename in os.listdir(examples_dir):
        if not filename.endswith(".pirtm"):
            continue
        
        input_file = os.path.join(examples_dir, filename)
        output_file = f"/tmp/{filename}.mlir"
        
        # Emit MLIR
        result = subprocess.run(
            ["python", "-m", "pirtm.transpiler.mlir_emitter", 
             "--input", input_file, "--output", output_file],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Emitter failed on {filename}:\n{result.stderr}"
        
        # Verify MLIR
        result = subprocess.run(
            ["mlir-opt", "--verify-diagnostics", output_file],
            capture_output=True, text=True
        )
        assert result.returncode == 0, f"Verification failed on {output_file}:\n{result.stderr}"
        
        # Check for mod= in output
        with open(output_file) as f:
            content = f.read()
            assert "mod=" in content, f"No mod= found in {output_file}"
            assert ".prime" not in content, f"Found .prime in {output_file} (should use mod=)"
        
        print(f"✅ {filename} → {output_file} (round-trip OK)")

if __name__ == "__main__":
    test_roundtrip_examples()
    print("✅ All examples round-trip successfully via mlir_emitter.py")
```

---

## Consequences

### Positive
- **Smooth Transition**: Old code continues working during migration window via shim
- **Atomic Day 14**: Clean cutover point after all refactoring is complete
- **Validated Migration**: Grep gates ensure no regressions; each file-level change is auditable
- **Spec Alignment**: MLIR output always matches ADR-004 (mod= nomenclature)
- **Foundation for Linking**: Day 14–16 linking gates depend on clean mod= usage

### Negative
- **Shim Maintenance**: Two weeks of dual-property API (technical debt)
- **Grep Gate Brittleness**: String matching can miss renamed-but-still-alive code
- **Manual Audit**: Per-file checklist requires human review to catch edge cases

---

## Alternatives Considered

### Alternative A: Big-Bang Rename (Day 0)

**Description**: Rename all `prime` → `mod` in a single PR before any gate passes.

**Rejection Reason**: 
1. High merge conflict risk during active development
2. Hard to review; changes span too many files
3. No intermediate validation checkpoints
4. Violates "gate order" principle (spec must be ready before implementation)

### Alternative B: No Shim; Immediate Migration

**Description**: Start migration on Day 0; old code breaks immediately.

**Rejection Reason**:
1. Blocks ADR-006 acceptance (verifier cannot test without MLIR input)
2. Creates merge conflicts during the critical Day 0–3 dialect window
3. Violates "support development productivity" principle

### Alternative C: Dual Codebase (keep both prime/ and mod/)

**Description**: Maintain two separate parallel implementations.

**Rejection Reason**:
1. Unsustainable technical debt
2. Bug fixes must be applied twice
3. Users cannot depend on both versions simultaneously
4. No clear path to eventual deprecation

---

## Rationale

The **shim + phased migration + grep gates** approach balances **safety** (no big-bang risk) with **momentum** (moving toward ADR-004 spec by Day 14).

The three phases are:
1. **Day 0–3**: Dialect is verified (ADR-006); shim makes old code work without changes
2. **Day 3–7**: Transpiler refactors to emit `mod=`; grep gate 1 validates
3. **Day 7–14**: Core layer migrates; examples round-trip; grep gate 2 validates
4. **Day 14**: Atomic rename; shim removed; Day 14–16 linker gates can begin

Each phase has a measurable gate; proceeding to the next phase is not allowed until the previous gate passes. This ensures the migration is traceable and reversible if needed.

---

## Acceptance Criteria

- [ ] `docs/migration/prime-to-mod-rename.md` exists with complete per-file audit table
- [ ] `src/pirtm/channels/shim.py` compiles and both `.prime` and `.mod` resolve correctly
- [ ] Day 3–7 Grep Gate 1 passes: `grep -r "\.prime\b"` returns 0 lines in active code
- [ ] Day 7–14 Grep Gate 2 passes: `grep -r "_prime\b"` returns 0 lines in active code
- [ ] All `.pirtm` files in `pirtm/examples/` round-trip via `mlir_emitter.py --output mlir` without error
- [ ] All MLIR output files contain `mod=` and no `.prime` references
- [ ] Day 14 atomic merge completes: `pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"` succeeds
- [ ] `test_roundtrip.py` passes all example files

**Day 0–3 Gate Status (ADR-006)**: ✅ PASSED → unlock Day 3–7  
**Day 3–7 Gate Status (This ADR, Grep Gate 1)**: ⏳ PENDING  
**Day 7–14 Gate Status (This ADR, Grep Gate 2)**: ⏳ PENDING  
**Day 14 Gate Status (Final Atomic Rename)**: ⏳ PENDING → unlock Day 14–16 (ADR-008)

---

## References

- [PIRTM ADR-004: MLIR Dialect Specification](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)
- [ADR-005: ADR Process + Directory Layout](./ADR-005-adr-process-layout.md)
- [ADR-006: Dialect Type-Layer Gate (Day 0–3)](./ADR-006-dialect-type-layer-gate.md)
- [docs/migration/prime-to-mod-rename.md](../migration/prime-to-mod-rename.md) — detailed per-file audit table
- [Structured Migration Planning](https://www.martinfowler.com/articles/patterns-of-distributed-systems/strangler-fig-pattern.html)

---

## Sign-Off

- [ ] Language Architect (PIRTM spec) approved
- [ ] Tooling Maintainer approved
- [ ] CI/Infra approved (adds grep gates to CI pipeline)
