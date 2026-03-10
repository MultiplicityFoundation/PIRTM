# Prime → Mod Migration Checklist (Day 0–14)

> **ADR Reference**: [ADR-007: Prime → Mod Migration + Shim Protocol](../adr/ADR-007-prime-mod-migration.md)  
> **Spec Reference**: [PIRTM ADR-004](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)  
> **Migration Window**: Mar 10 (Day 0) – Mar 24 (Day 14)

---

## Overview

This document tracks the atomic rename from `prime` to `mod` nomenclature across three code layers, with per-file migration status and precise acceptance gates.

**Key Constraint (L0 Invariant #1)**: `pirtm.module` carries exactly one `prime_index`, one `epsilon`, one `op_norm_T`. The field name `prime_index` does NOT change; only the internal modulus property (`mod=`) is unified.

---

## Tier 1: MLIR Dialect Layer (Day 0–3, Locked after ADR-006)

| File | Change | Status | Spec Requirement |
| :--- | :--- | :--- | :--- |
| `src/pirtm/dialect/pirtm.td` | TableGen: all types use `mod=` in parameters | ✅ DONE (ADR-006) | ADR-004: `!pirtm.cert(mod=p)` |
| `src/pirtm/dialect/pirtm_types.cpp` | Verifier checks `int64_t mod` parameter | ✅ DONE (ADR-006) | ADR-004: Miller-Rabin on all `mod=` |

**Gate Status (Day 0–3)**:
```bash
mlir-opt --verify-diagnostics pirtm/tests/pirtm-types-basic.mlir
# Expected: PASS (all four test cases)
```

---

## Tier 2: Channel Layer (Day 0–7, Shim Active)

### Files to Create (Shim API)

| File | Purpose | Status |
| :--- | :--- | :--- |
| `src/pirtm/channels/shim.py` | Backward-compat shim; provides `.prime` and `.mod` properties | ⏳ TO DO |

### Files to Refactor

| File | Changes | Grep Gate | Status |
| :--- | :--- | :--- | :--- |
| `src/pirtm/channels/base.py` | Add `@property def mod(self)` to existing class; keep `.prime` via shim | `grep "\.prime" base.py` → 0 lines | ⏳ TO DO |
| `src/pirtm/channels/pirtm_channel.py` | Constructor: store as `self._mod`; expose via `.mod` property; shim provides `.prime` | `grep "\.prime" pirtm_channel.py` → 0 lines | ⏳ TO DO |

### Shim Protocol

```python
# Before (old code, still works via shim):
channel = PrimeChannel(prime=7)
assert channel.prime == 7

# After shim and refactor (new code):
channel = PrimeChannel(mod=7)
assert channel.mod == 7
assert channel.prime == 7  # shim compatibility

# Post-Day 14 (shim removed):
channel = PrimeChannel(mod=7)
assert channel.mod == 7  # .prime no longer exists
```

**Shim Details**:
- Old code: `channel.prime` → returns `channel._mod`
- New code: `channel.mod` → returns `channel._mod`
- Both are valid during migration window
- No breaking changes to existing callers

---

## Tier 3: Transpiler Layer (Day 3–7)

### Files to Refactor

| File | Changes | Grep Gate | Details | Status |
| :--- | :--- | :--- | :--- | :--- |
| `src/pirtm/transpiler/mlir_emitter.py` | **Emit `mod=` in all MLIR output**; internal variables may use `_mod` for clarity | `grep -E "(\.prime\|_prime)" mlir_emitter.py \| wc -l` → 0 | All type constructors use `mod=mod_value` syntax; no `.prime` property access | ⏳ TO DO |
| `src/pirtm/transpiler/parser.py` | **Parse `mod=` from input**; convert to internal `_mod` attribute; update MLIR assembly parsing | `grep -E "(\.prime\|_prime)" parser.py \| wc -l` → 0 | All type parsers recognize `!pirtm.cert(mod=...)` syntax | ⏳ TO DO |

### Migration Example

**Before (using `.prime`):**
```python
# mlir_emitter.py
cert = CertType(mod=channel.prime)  # ❌ relies on .prime
emit_mlir(f"!pirtm.cert(prime={cert.mod})")  # ❌ emits old syntax
```

**After (using `.mod`):**
```python
# mlir_emitter.py
cert = CertType(mod=channel.mod)  # ✅ uses .mod directly
emit_mlir(f"!pirtm.cert(mod={cert.mod})")  # ✅ emits spec-compliant syntax
```

**Gate Status (Day 3–7, Grep Gate 1)**:
```bash
grep -r "\.prime\b" pirtm/ --include="*.py" | grep -v "__pycache__" | wc -l
# Expected: 0 lines
```

---

## Tier 4: Core Algorithm Layer (Day 7–14)

### Files to Refactor

| File | Changes | Grep Gate | Details | Status |
| :--- | :--- | :--- | :--- | :--- |
| `src/pirtm/core/contractivity.py` | Use `.mod` for contractivity matrix construction; remove all `.prime` references | `grep -E "\.prime\b" contractivity.py` → 0 lines | All modulus lookups use `session_graph.prime_index` or type `.mod` param | ⏳ TO DO |
| `src/pirtm/core/projection.py` | Use `.mod` for spectral projection setup; remove all `.prime` references | `grep -E "\.prime\b" projection.py` → 0 lines | All projections initialized via `mod=` type parameter | ⏳ TO DO |
| `src/pirtm/core/gain.py` | Use `.mod` for spectral radius / small-gain computation | `grep -E "\.prime\b" gain.py` → 0 lines | All gains indexed by `mod`, not `prime` | ⏳ TO DO |

### Acceptance Tests

Create `pirtm/tests/test_roundtrip.py`:

```python
def test_all_examples_roundtrip():
    """Every .pirtm file in pirtm/examples/ must round-trip cleanly."""
    for fname in os.listdir("pirtm/examples"):
        if not fname.endswith(".pirtm"):
            continue
        result = subprocess.run(
            ["python", "-m", "pirtm.transpiler.mlir_emitter", 
             "--input", f"pirtm/examples/{fname}",
             "--output", f"/tmp/{fname}.mlir"],
            capture_output=True
        )
        assert result.returncode == 0, f"Emitter failed: {result.stderr}"
        
        # Verify MLIR
        result = subprocess.run(
            ["mlir-opt", "--verify-diagnostics", f"/tmp/{fname}.mlir"],
            capture_output=True
        )
        assert result.returncode == 0, f"Verification failed: {result.stderr}"
```

**Gate Status (Day 7–14, Grep Gate 2)**:
```bash
grep -r "_prime\b" pirtm/ --include="*.py" | grep -v "__pycache__" | wc -l
# Expected: 0 lines (no internal _prime attributes in active code)
```

**Day 7–14 Acceptance**:
```bash
python -m pytest pirtm/tests/test_roundtrip.py -v
# Expected: All examples pass round-trip validation
```

---

## Tier 5: Linking Layer (Day 14–16, Locked after Day 14)

| File | Changes | Status | Spec Requirement |
| :--- | :--- | :--- | :--- |
| `src/pirtm/transpiler/pirtm_link.py` | All inputs now use `mod=`; no `.prime` or `_prime` conversions needed | ✅ AUTOMATIC (after Tier 4) | ADR-004: link-time `session_graph` carries `mod=` from transpile time |

**Gate Status (Day 14)**:
```bash
pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"
# Expected: PASS (verifier confirms all modules use valid mod values)
```

---

## Grep Gate Commands (Copy-Paste Ready)

### Gate 1 (Day 3–7): Transpiler Layer Complete

```bash
#!/bin/bash
set -e

echo "=== Grep Gate 1: Transpiler Layer (Day 3–7) ==="
echo "Checking for .prime property access (should be 0 lines)..."

count=$(grep -r "\.prime\b" pirtm/ --include="*.py" \
  | grep -v "__pycache__" \
  | grep -v ".pyc" \
  | grep -v "# COMPAT:" \
  | wc -l)

if [ "$count" -eq 0 ]; then
  echo "✅ PASS: No .prime property access in active code"
  exit 0
else
  echo "❌ FAIL: Found $count .prime references. Files:"
  grep -r "\.prime\b" pirtm/ --include="*.py" \
    | grep -v "__pycache__" \
    | grep -v ".pyc"
  exit 1
fi
```

### Gate 2 (Day 7–14): Core Layer Complete

```bash
#!/bin/bash
set -e

echo "=== Grep Gate 2: Core Algorithm Layer (Day 7–14) ==="
echo "Checking for _prime internal attributes (should be 0 lines)..."

count=$(grep -r "_prime\b" pirtm/ --include="*.py" \
  | grep -v "__pycache__" \
  | grep -v ".pyc" \
  | grep -v "# COMPAT:" \
  | wc -l)

if [ "$count" -eq 0 ]; then
  echo "✅ PASS: No _prime attributes in active code"
  exit 0
else
  echo "❌ FAIL: Found $count _prime references. Files:"
  grep -r "_prime\b" pirtm/ --include="*.py" \
    | grep -v "__pycache__" \
    | grep -v ".pyc"
  exit 1
fi
```

### Gate 3 (Day 14): Atomic Merge Complete

```bash
#!/bin/bash
set -e

echo "=== Grep Gate 3: Atomic Merge Complete (Day 14) ==="

# Check 1: No residual .prime or _prime
echo "Checking for any residual nomenclature..."
count=$(grep -r "\.prime\b\|_prime\b" pirtm/ --include="*.py" \
  | grep -v "__pycache__" \
  | grep -v ".pyc" \
  | wc -l)

if [ "$count" -ne 0 ]; then
  echo "❌ FAIL: Found residual naming ($count lines)"
  grep -r "\.prime\b\|_prime\b" pirtm/ --include="*.py" | head -20
  exit 1
fi

# Check 2: Contractivity verification passes
echo "Checking contractivity verifier..."
pirtm inspect basic.pirtm.bc | grep -q "contractivity_check: PASS" || {
  echo "❌ FAIL: contractivity_check did not pass"
  exit 1
}

echo "✅ PASS: Atomic merge complete"
echo "  - No .prime or _prime nomenclature remains"
echo "  - contractivity_check: PASS"
exit 0
```

---

## Per-Phase Summary

| Phase | Dates | Owner | Gate | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | Mar 10–13 (Day 0–3) | Dialect Team | `mlir-opt --verify-diagnostics` on basic types | ✅ ADR-006 |
| **Phase 2** | Mar 13–17 (Day 3–7) | Transpiler Team | Grep Gate 1: no `.prime` refs | ⏳ ADR-007 |
| **Phase 3** | Mar 17–24 (Day 7–14) | Core Team | Grep Gate 2: no `_prime` attrs + all examples round-trip | ⏳ ADR-007 |
| **Phase 4** | Mar 24 (Day 14) | All | Atomic merge: shim removed, Grep Gate 3 passes | ⏳ ADR-008 |

---

## FAQ

**Q: Can we rename everything on Day 0?**  
A: No. ADR-005 mandates "gate order": dialect must pass (Day 0–3) before transpiler migrates. Big-bang renames during dialect development risk breaking the acceptance test.

**Q: What if old code uses `channel.prime`?**  
A: During Days 0–14, the shim makes it work via property mapping. After Day 14, the shim is removed and `.prime` will fail (drives migration urgency).

**Q: Can I use `mod` and `prime` interchangeably?**  
A: Yes, during the migration window via the shim. After Day 14, only `mod` and `prime_index` (field name) are valid.

**Q: What if Grep Gate 1 fails?**  
A: You're still accessing `.prime` somewhere in the transpiler. Find the file and refactor it to use `.mod` instead.

**Q: Do I need to rename the `prime_index` field?**  
A: **No.** L0 invariant #1 locks the field name as `prime_index`. Only the internal `.mod` property is renamed.

---

## Rollback Plan

If migration fails and needs rollback:

1. **Revert to commit before Day 3–7 merge**: Shim is still active; old code works again
2. **Keep ADR-6 (dialect types)**: The dialect gate passed and is decoupled from nomenclature
3. **Retry migration** on next iteration with lessons learned

The phased approach makes rollback safe—each phase can be reverted independently.

---

## Sign-Off Checklist

- [ ] Day 0–3: Dialect gate passes (`mlir-opt --verify-diagnostics`)
- [ ] Day 3–7: Transpiler migrated; Grep Gate 1 passes  
- [ ] Day 7–14: Core layer migrated + examples round-trip; Grep Gate 2 passes
- [ ] Day 14: Atomic merge; Grep Gate 3 passes; shim removed
- [ ] Day 14–16: Linker gates can begin (ADR-008)
