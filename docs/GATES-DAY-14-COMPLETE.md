# ADR-007 Day 14 Gate: Contractivity Check Complete

**Date**: March 10, 2026  
**Status**: ✅ **DAY 14 GATE PASSED**

---

## Summary

The **Day 14 gate** validates contractivity verification at transpile time via bytecode serialization and inspection. All modules must satisfy the contractivity constraint: $\|\!T\!\| + \varepsilon < 1$.

### Gate Result

| Requirement | Status | Evidence |
| :--- | :---: | :--- |
| `pirtm inspect basic.pirtm.bc \| grep "contractivity_check: PASS"` | ✅ PASS | test_day_14_contractivity.py |
| Contractivity verification logic | ✅ 3/3 test cases | Contractive, marginal, divergent systems |
| Bytecode format & serialization | ✅ PASS | Round-trip bytecode load/save |
| Inspection tool output | ✅ PASS | Correct diagnostic format |
| End-to-end workflow | ✅ PASS | Examples → MLIR → bytecode → inspect |

---

## Files Created

### 1. Bytecode Format
- **[pirtm/transpiler/pirtm_bytecode.py](pirtm/transpiler/pirtm_bytecode.py)** (300+ lines) — Bytecode serialization and contractivity check pass

### 2. Inspection Tool
- **[pirtm/tools/pirtm_inspect.py](pirtm/tools/pirtm_inspect.py)** (120+ lines) — Tool to inspect bytecode files

### 3. Test Suites
- **[pirtm/tests/test_day_14_contractivity.py](pirtm/tests/test_day_14_contractivity.py)** (5 test cases)
- **[pirtm/tests/demo_day_14_workflow.py](pirtm/tests/demo_day_14_workflow.py)** (end-to-end demo)

---

## Contractivity Verification

### Mathematical Foundation

A system is **contractive** if the final state remains bounded:

$$\|q_t\| < 1 - \varepsilon$$

This requires:
$$\|T\| + \varepsilon < 1$$

**Verification margin**: $1 - \varepsilon - \|T\| > 0$

### Test Results

| System | ε | ‖T‖ | Margin | Status |
|:---|:---:|:---:|:---:|:---:|
| **Contractive** | 0.05 | 0.90 | 0.05 | ✅ PASS |
| **Marginally stable** | 0.05 | 0.95 | 0.00 | ❌ FAIL |
| **Divergent** | 0.05 | 1.10 | -0.15 | ❌ FAIL |

---

## Bytecode Format (.pirtm.bc)

**Structure**: JSON with embedded MLIR text and proof information

```json
{
  "format": "pirtm.bc",
  "version": "1.0",
  "timestamp": "2026-03-10T...",
  "content": {
    "modules": [
      {
        "name": "linear_recurrence",
        "prime_index": 7919,
        "epsilon": 0.05,
        "op_norm_T": 0.90,
        "contractivity_check": "PASS",
        "proof_hash": "0xfe4b8fb156e57b56..."
      }
    ],
    "coupling": "#pirtm.unresolved_coupling",
    "mlir_source": "module @linear_recurrence { ... }",
    "audit_trail": ["Day 14: contractivity_check pass completed"]
  }
}
```

### Key Fields

- **proof_hash**: Deterministic SHA256(prime_index ∥ ε ∥ ‖T‖ ∥ nonce)
- **contractivity_check**: "PASS" if margin > 0, else "FAIL"
- **coupling**: L0 invariant #4 (unresolved at transpile time)
- **audit_trail**: Transformation history

---

## Inspection Tool Usage

### Basic Inspection

```bash
python3 pirtm/tools/pirtm_inspect.py basic.pirtm.bc
```

**Output**:
```
PIRTM Bytecode Inspection Report
File: basic.pirtm.bc

Module Status:
──────────────────────────────────────────────────────────
✅ linear_recurrence     mod=7919 ε=0.0500 ‖T‖=0.9000 contractivity_check: PASS
──────────────────────────────────────────────────────────
✅ contractivity_check: PASS
```

### Verbose Inspection

```bash
python3 pirtm/tools/pirtm_inspect.py -v basic.pirtm.bc
```

Includes:
- Proof hash values
- Margin analysis per module
- Audit trail details

---

## Implementation Details

### ContractivityCheckPass

Transpile-time verification pass:

```python
status, reason = ContractivityCheckPass.check_module(
    module_name="linear_recurrence",
    prime_index=7919,
    epsilon=0.05,
    op_norm_T=0.90,
)
# Returns ("PASS", "Contractive: margin = ... > 0")
```

### Bytecode Generation Workflow

```python
# 1. Emit MLIR
mlir = emitter.emit_module("linear_recurrence")

# 2. Generate bytecode with contractivity checks
bytecode = create_bytecode_from_mlir(mlir, modules)

# 3. Write to .pirtm.bc file
bytecode.write_to_file(Path("basic.pirtm.bc"))

# 4. Inspect via tool
result = PIRTMInspector.inspect_file(Path("basic.pirtm.bc"))
```

---

## Test Results Summary

### Unit Tests (5/5 passing)

1. **Contractive System** ✅
   - ε=0.05, ‖T‖=0.90, margin=0.05
   - Result: PASS (as expected)

2. **Marginally Stable System** ✅
   - ε=0.05, ‖T‖=0.95, margin=0.00
   - Result: FAIL (correct rejection)

3. **Divergent System** ✅
   - ε=0.05, ‖T‖=1.10, margin=-0.15
   - Result: FAIL (correct rejection)

4. **Bytecode Generation & Inspection** ✅
   - Generate bytecode from MLIR
   - Write to file, read back
   - Verify round-trip proof hash

5. **Inspection Tool Output** ✅
   - Correct diagnostic format
   - "contractivity_check: PASS" appears in output
   - Exit code 0 for all-pass

### Integration Tests (2/2 examples)

1. **basic_contractive_system.json** ✅
   - Single module: linear_recurrence
   - mod=7919, ε=0.05, ‖T‖=0.90
   - Result: contractivity_check: PASS

2. **multimodule_network.json** ✅
   - Two modules: module_A, module_B
   - Both contractive (margins: 0.13, 0.07)
   - Result: contractivity_check: PASS

---

## L0 Invariant #2 Verification

**Requirement**: contractivity-check runs at transpile time

**Implementation**:
- ✅ Runs during bytecode generation (before linking)
- ✅ Enforces margin > 0: `1 - ε - ‖T‖ > 0`
- ✅ Reports differential: `margin = 1 - ε - ‖T‖`
- ✅ Fails fast: divergent/marginal systems rejected

---

## Gate Specifications

### Target Requirement

```bash
pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"
```

**Expected Output**:
```
✅ contractivity_check: PASS
```

**Exit Code**: 0 (all modules verified)

---

## Next Phase: Day 14-16 (Commitment Collision)

The next gate (ADR-008) requires:

```
Commitment-collision test passes
```

### Requirements

- Identity commitment computation for each module
- Duplicate detection in `coupling.json`
- Diagnostic: `error: duplicate identity_commitment`

### Blocking

- Day 14 gate (✅ complete) unlocks Day 14-16
- Day 14-16 requires: transpile-time contractivity (Day 14) + link-time coupling validation

---

## Verification Commands

```bash
# Run all Day 14 tests
python3 /workspaces/Tooling/pirtm/tests/test_day_14_contractivity.py

# Run end-to-end workflow demo
python3 /workspaces/Tooling/pirtm/tests/demo_day_14_workflow.py

# Inspect example bytecode
python3 /workspaces/Tooling/pirtm/tools/pirtm_inspect.py BYTECODE_FILE
```

---

## Status

**Ready to proceed to Day 14-16**: ✅ YES

All gates from Day 0-14 are complete and passing:
- ✅ Day 0-3: Type-layer verification
- ✅ Day 3-7: Coprime merge validation
- ✅ Day 7-14: Transpiler round-trip
- ✅ Day 14: Contractivity verification
