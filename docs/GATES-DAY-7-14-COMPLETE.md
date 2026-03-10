# ADR-007 Day 7-14 Gate: Transpiler Round-Trip Complete

**Date**: March 10, 2026  
**Status**: ✅ **DAY 7-14 GATE PASSED**

---

## Summary

The **Day 7-14 gate** validates that all example PIRTM programs can round-trip through the transpiler via `mlir_emitter.py`, emitting valid MLIR with canonical `mod=` syntax.

### Gate Result

| Requirement | Status | Evidence |
| :--- | :---: | :--- |
| All examples/ round-trip via `mlir_emitter.py --output mlir` | ✅ 4/4 | [test_day_7_14_round_trip.py](tests/test_day_7_14_round_trip.py) |
| Single-module example (basic) | ✅ PASS | basic_contractive_system.json |
| Multi-module example (coprime) | ✅ PASS | multimodule_network.json |
| Composite modulus example | ✅ PASS | composite_modulus_system.json |
| Coupled system example | ✅ PASS | tightly_coupled_system.json |

---

## Files Created

### 1. Example Programs
- **[examples/basic_contractive_system.json](examples/basic_contractive_system.json)** — Single-module with prime modulus
- **[examples/multimodule_network.json](examples/multimodule_network.json)** — Two-module network (coprime, L0 #1)
- **[examples/composite_modulus_system.json](examples/composite_modulus_system.json)** — Squarefree composite (L0 #5)
- **[examples/tightly_coupled_system.json](examples/tightly_coupled_system.json)** — Multiversal coupling test

### 2. Test Suite
- **[tests/test_day_7_14_round_trip.py](tests/test_day_7_14_round_trip.py)** — Comprehensive round-trip validator (248 lines)

---

## Test Results

### Example 1: basic_contractive_system
```
mod=7919  ε=0.05  ‖T‖=0.90
  ✅ Structure validation
  ✅ MLIR emission (4 mod= declarations)
  ✅ Canonical form (no .prime)
  ✅ L0 invariant #4 (unresolved coupling)
```

### Example 2: multimodule_network
```
module_A: mod=7919  ε=0.12  ‖T‖=0.75
module_B: mod=8191  ε=0.08  ‖T‖=0.85
Coprimality: gcd(7919, 8191) = 1 ✅
  ✅ Structure validation
  ✅ MLIR emission (8 mod= declarations)
  ✅ Canonical form (no .prime)
  ✅ L0 invariant #1 (coprime modules)
```

### Example 3: composite_modulus_system
```
mod=30 (squarefree: 2×3×5)  ε=0.10  ‖T‖=0.60
Möbius: μ(30) = -1 ≠ 0 ✅
  ✅ Structure validation
  ✅ MLIR emission (4 mod= declarations)
  ✅ Canonical form (no .prime)
  ✅ L0 invariant #5 (squarefree composite)
```

### Example 4: tightly_coupled_system
```
coupled_module_1: mod=11  ε=0.20  ‖T‖=0.50
coupled_module_2: mod=13  ε=0.15  ‖T‖=0.60
Coprimality: gcd(11, 13) = 1 ✅
  ✅ Structure validation
  ✅ MLIR emission (8 mod= declarations)
  ✅ Canonical form (no .prime)
  ✅ L0 invariant #1 (coprime network)
```

---

## Validation Checks

Each example is validated for:

1. **Structure Validation**
   - JSON schema compliance (name, description, components)
   - Required fields: `prime_index`, `epsilon`, `op_norm_T`
   - Type correctness: epsilon ∈ [0,1], op_norm_T ≥ 0
   - Primality: mod= values pass Miller-Rabin (or squarefree test)
   - Coprimality: Multi-module systems satisfy gcd = 1 (L0 #1)

2. **MLIR Emission**
   - Emitter successfully creates valid MLIR modules
   - No exceptions or runtime errors
   - Output is non-empty string

3. **MLIR Validation**
   - ✅ Uses `mod=` canonical syntax (not `.prime`)
   - ✅ Uses `!pirtm.cert(mod=...)`, `!pirtm.epsilon(mod=...)`, etc.
   - ✅ Coupling is `#pirtm.unresolved_coupling` (L0 #4)
   - ✅ Valid module structure
   - ✅ No legacy property access patterns

---

## L0 Invariants Validated

| Invariant | Test Case | Status |
| :--- | :--- | :---: |
| **#1**: Coprimality (gcd=1) | multimodule_network, tightly_coupled_system | ✅ Enforced |
| **#3**: Prime mod= on atomic types | all 4 examples | ✅ Verified |
| **#4**: Unresolved coupling at transpile | all 4 examples | ✅ Present |
| **#5**: Squarefree composites | composite_modulus_system | ✅ Verified |

---

## Round-Trip Semantics

The round-trip flow validates:

```
JSON Example → Structure Validation → MLIR Emission → MLIR Validation → ✅ PASS
     ↓              ↓                    ↓                ↓
  Schema        Primes, primes        mod= syntax    No .prime refs
  Coprimality   Squarefree comp       Valid types    Coupling unresolved
  Fields        L0 invariants         Modules        L0 invariants
```

---

## Design Notes

### Example Format (JSON)
Each example follows this schema:
```json
{
  "name": "example_name",
  "description": "Human-readable description",
  "spec_reference": "Related ADR or requirement",
  "components": [
    {
      "name": "component_name",
      "prime_index": 7919,
      "epsilon": 0.05,
      "op_norm_T": 0.9,
      "description": "Component description"
    }
  ]
}
```

### Validator Design
The `RoundTripTestSuite` class:
- Loads examples from `pirtm/examples/*.json`
- Validates structure and L0 invariants
- Emits MLIR via `PIRTMMLIREmitter`
- Validates emitted MLIR against canonical form spec
- Reports detailed pass/fail for each example

---

## Next Phase: Day 14+

The next gates (Day 14 onward) require:

```
Day 14   | pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"
Day 14-16 | Commitment-collision test passes
Day 30   | r=0.7 link passes; r=1.1 link fails with diagnostic
```

**Blocking requirement**: Day 7-14 gate (✅ complete) must pass before proceeding.

---

## Verification Commands

```bash
# Run the Day 7-14 round-trip test
python3 /workspaces/Tooling/pirtm/tests/test_day_7_14_round_trip.py

# Run all gates (Days 0-7 and 7-14)
python3 /workspaces/Tooling/pirtm/tests/mlir_diagnostic_verifier.py
python3 /workspaces/Tooling/pirtm/tests/test_day_3_7_coprime_merge.py
python3 /workspaces/Tooling/pirtm/tests/test_day_7_14_round_trip.py
python3 /workspaces/Tooling/pirtm/tools/grep_gates.py all
```

---

## Status

**Ready to proceed to Day 14+**: ✅ YES

All gates passed:
- ✅ Day 0-3: Type-layer verification
- ✅ Day 3-7: Coprime merge validation
- ✅ Day 7-14: Transpiler round-trip (4/4 examples)
- ✅ Grep gates: Migration validation (0 violations)
