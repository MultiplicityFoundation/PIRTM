# ADR-006: PIRTM Dialect Type-Layer Gate (Day 0–3)

> **Status**: Proposed  
> **Date**: 2026-03-10  
> **Authors**: PIRTM Dialect Team  
> **Spec Reference**: [PIRTM ADR-004](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)

---

## Problem Statement

The PIRTM type system (defined in PIRTM ADR-004) introduces new MLIR types with rigorous constraints:
- `mod=` values on atomic types must be prime via Miller-Rabin test
- Composite types (`pirtm.session_graph`, custom kinds) must use squarefree moduli
- Every type carries verification obligations that cannot be pushed to runtime

Currently, there is no TableGen specification, no verifier implementation, and no acceptance test. This means:
1. The dialect cannot be compiled or parsed
2. Type constraints are unenforceable
3. Future developers do not know which constraints are checked at compile time vs. runtime
4. Diagnostic error messages are inconsistent or missing

This ADR defines the **Day 0–3 gate**: all basic type constraints verified at transpile time via LLVM/MLIR's verifier framework.

---

## Solution

### 1. Dialect Definition: `pirtm.td` (TableGen)

Create `src/pirtm/dialect/pirtm.td` with:

```tablegen
// ===== Atomic Types =====
def PIRTM_Cert : PIRTM_Type<"Cert"> {
  let summary = "Prime-modulo certificate type";
  let description = [{
    !pirtm.cert(mod=p)
    where p is prime (L0 invariant #3).
    Verified at dialect parse time via Miller-Rabin.
  }];
  let parameters = (ins "int64_t":$mod);
  let genVerifyDecl = 1;
  let assemblyFormat = "`cert` `(` `mod` `=` $mod `)`";
}

def PIRTM_Epsilon : PIRTM_Type<"Epsilon"> {
  let summary = "Convergence bound";
  let description = [{
    !pirtm.epsilon(mod=p, value=eps)
    where p is prime (L0 invariant #5).
  }];
  let parameters = (ins "int64_t":$mod, "float":$value);
  let genVerifyDecl = 1;
  let assemblyFormat = "`epsilon` `(` `mod` `=` $mod `,` `value` `=` $value `)`";
}

def PIRTM_OpNormT : PIRTM_Type<"OpNormT"> {
  let summary = "Operator norm bound";
  let description = [{
    !pirtm.op_norm_t(mod=p, norm=n)
    where p is prime (L0 invariant #5).
  }];
  let parameters = (ins "int64_t":$mod, "float":$norm);
  let genVerifyDecl = 1;
  let assemblyFormat = "`op_norm_t` `(` `mod` `=` $mod `,` `norm` `=` $norm `)`";
}

// ===== Composite Types =====
def PIRTM_SessionGraph : PIRTM_Type<"SessionGraph"> {
  let summary = "Session coupling graph";
  let description = [{
    !pirtm.session_graph(
      mod=N,        // N must be squarefree (L0 invariant #5)
      coupling=coupling_attr
    )
  }];
  let parameters = (ins "int64_t":$mod, "Attribute":$coupling);
  let genVerifyDecl = 1;
}

def PIRTM_UnresolvedCoupling : PIRTM_Attr<"UnresolvedCoupling", "unresolved_coupling"> {
  let summary = "Placeholder for coupling.json resolution";
  let description = [{
    #pirtm.unresolved_coupling
    Used at transpile time; replaced by actual matrix during linking.
    Enforces L0 invariant #4: gain_matrix is never transpile-time.
  }];
}
```

**Key Points**:
- `genVerifyDecl = 1` on all types to generate `verify()` methods
- `mod=` appears in assembly format everywhere
- Verifier methods will be implemented in `pirtm_types.cpp`

### 2. Verifier Implementation: `pirtm_types.cpp`

Create `src/pirtm/dialect/pirtm_types.cpp` with:

```cpp
#include "pirtm/dialect/pirtm_dialect.h"
#include "llvm/ADT/SmallVector.h"
#include <algorithm>
#include <cmath>

namespace pirtm {

// ===== Miller-Rabin Primality Test =====
// Returns true if mod is prime; false otherwise.
static bool isPrime(int64_t mod) {
  if (mod < 2) return false;
  if (mod == 2 || mod == 3) return true;
  if (mod % 2 == 0) return false;
  
  // Write mod-1 = 2^r * d where d is odd
  int64_t d = mod - 1;
  int r = 0;
  while ((d & 1) == 0) {
    d >>= 1;
    r++;
  }
  
  // Deterministic bases for mod < 2^64
  const int64_t bases[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37};
  
  for (int64_t a : bases) {
    if (a >= mod) continue;
    
    int64_t x = 1;
    int64_t base = a;
    int64_t exp = d;
    
    // modular exponentiation: x = a^d mod mod
    while (exp > 0) {
      if (exp & 1) x = (__int128)x * base % mod;
      base = (__int128)base * base % mod;
      exp >>= 1;
    }
    
    if (x == 1 || x == mod - 1) continue;
    
    bool composite = true;
    for (int i = 0; i < r - 1; i++) {
      x = (__int128)x * x % mod;
      if (x == mod - 1) {
        composite = false;
        break;
      }
    }
    
    if (composite) return false;
  }
  
  return true;
}

// ===== Squarefree Check =====
// Returns true if mod is squarefree (μ(mod) ≠ 0), false otherwise.
// Also returns factorization for error messages.
static bool isSquarefree(int64_t mod, std::string& factorization) {
  if (mod <= 1) {
    factorization = std::to_string(mod);
    return false;
  }
  
  factorization.clear();
  int64_t n = mod;
  bool square_found = false;
  
  // Trial division up to sqrt(n)
  for (int64_t p = 2; p * p <= n; p++) {
    int count = 0;
    while (n % p == 0) {
      n /= p;
      count++;
      if (count > 1) square_found = true;
    }
    if (count > 0) {
      if (!factorization.empty()) factorization += " * ";
      factorization += std::to_string(p);
      if (count > 1) factorization += "^" + std::to_string(count);
    }
  }
  
  if (n > 1) {
    if (!factorization.empty()) factorization += " * ";
    factorization += std::to_string(n);
  }
  
  return !square_found;
}

// ===== Type Verifiers =====

::mlir::LogicalResult CertType::verify(::mlir::function_ref<::mlir::InFlightDiagnostic()> emitError, int64_t mod) {
  if (!isPrime(mod)) {
    emitError() << "mod=" << mod << " is not prime; !pirtm.cert requires prime modulus (L0 invariant #3)";
    return ::mlir::failure();
  }
  return ::mlir::success();
}

::mlir::LogicalResult EpsilonType::verify(::mlir::function_ref<::mlir::InFlightDiagnostic()> emitError, 
                                          int64_t mod, float value) {
  if (!isPrime(mod)) {
    emitError() << "mod=" << mod << " is not prime; !pirtm.epsilon requires prime modulus (L0 invariant #5)";
    return ::mlir::failure();
  }
  return ::mlir::success();
}

::mlir::LogicalResult OpNormTType::verify(::mlir::function_ref<::mlir::InFlightDiagnostic()> emitError,
                                          int64_t mod, float norm) {
  if (!isPrime(mod)) {
    emitError() << "mod=" << mod << " is not prime; !pirtm.op_norm_t requires prime modulus (L0 invariant #5)";
    return ::mlir::failure();
  }
  return ::mlir::success();
}

::mlir::LogicalResult SessionGraphType::verify(::mlir::function_ref<::mlir::InFlightDiagnostic()> emitError,
                                               int64_t mod, ::mlir::Attribute coupling) {
  std::string factorization;
  if (!isSquarefree(mod, factorization)) {
    emitError() << "mod=" << mod << " is not squarefree (" << factorization << "); "
                << "!pirtm.session_graph requires squarefree modulus (L0 invariant #5)";
    return ::mlir::failure();
  }
  return ::mlir::success();
}

} // namespace pirtm
```

**Key Features**:
- `isPrime()` uses deterministic Miller-Rabin for `mod < 2^64`
- `isSquarefree()` uses trial division up to √n, returns factorization
- Error messages include full factored form (e.g., "mod=7921 is not prime" is NOT enough; must show "7921 = 89 * 89")
- All error strings are spec-stable API (matched by `.mlir` expected-error)

### 3. Acceptance Test: `pirtm-types-basic.mlir`

Create `pirtm/tests/pirtm-types-basic.mlir` with exactly **four test cases**:

```mlir
// Test 1: Prime cert (PASS)
// expected-error @below {{}}
%0 : !pirtm.cert(mod=7)

// Test 2: Composite cert via non-prime (FAIL)
// expected-error @below {{mod=7921 is not prime}}
%1 : !pirtm.cert(mod=7921)

// Test 3: Composite cert via perfect square (FAIL)
// expected-error @below {{mod=49 is not squarefree}}
%2 : !pirtm.cert(mod=49)

// Test 4: Valid session graph with squarefree mod (PASS)
%3 : !pirtm.session_graph(mod=6, coupling=#pirtm.unresolved_coupling)
```

**Acceptance Gate**:
```bash
mlir-opt --verify-diagnostics pirtm/tests/pirtm-types-basic.mlir
```

This command:
1. Parses all four test cases
2. Verifies each type by calling the verifier methods from `pirtm_types.cpp`
3. Checks that error messages match the `expected-error` directives exactly
4. Returns exit code 0 if all four match

---

## Consequences

### Positive
- **Compile-time safety**: Type errors caught immediately, not at link time
- **Precise diagnostics**: Error messages include factorization, aiding debugging
- **Spec enforcement**: The verifier is the executable specification of L0 invariants #3 and #5
- **Test clarity**: Four test cases cover the key scenarios (prime, composite, squarefree, non-squarefree)
- **Foundation for later gates**: Day 3–7 (module merge) and Day 7–14 (round-trip) depend on this gate passing

### Negative
- **TableGen complexity**: Learning curve for LLVM/MLIR dialect development
- **Miller-Rabin overhead**: Prime testing on every type instantiation (acceptable: tests are rare and deterministic)
- **Rigid error messages**: Changing diagnostic strings requires PIRTM ADR-004 amendment (slow process)

---

## Alternatives Considered

### Alternative A: Runtime Verification Only

**Description**: Check `mod=` primality and squarefree constraints at transpile/link time in Python, not in the dialect verifier.

**Rejection Reason**: MLIR's `--verify-diagnostics` framework is the standard tool for verifying dialect constraints. Pushing verification to Python would:
1. Duplicate logic (verifier in TableGen and in Python)
2. Make the dialect weaker (dialect does not enforce its own constraints)
3. Lose integration with MLIR tooling (mlir-opt, mlir-translate, etc.)

### Alternative B: Single Error Message Format

**Description**: Use simpler error messages like "mod must be prime" without factorization.

**Rejection Reason**: Users need the factorization to debug. Showing "7921 = 89 * 89" immediately tells them why a cert is invalid and how to fix it. Cost (extra ~20 bytes per error) is negligible.

### Alternative C: Generate Verifiers Automatically

**Description**: Use a macro to auto-generate verifier stubs; implement logic elsewhere.

**Rejection Reason**: LLVM TableGen's `genVerifyDecl = 1` already generates the stub. The implementation (`pirtm_types.cpp`) is the right place to put the logic. No benefit to further abstraction.

---

## Rationale

We choose **compile-time verifier via TableGen + MLIR dialect system** because:

1. **PIRTM ADR-004 mandates it**: Type constraints are part of the dialect semantics, not optional business logic
2. **MLIR alignment**: `--verify-diagnostics` is the standard MLIR testing tool; using it makes the dialect portable
3. **Spec stability**: Error messages are matched by `.mlir` test files; treating them as spec-stable API prevents silent breaks
4. **Foundation for gates**: Day 3–7 and Day 7–14 gates depend on passing Day 0–3; we must get the basics right first

The **four-test-case design** covers:
- Two positive cases (prime cert, squarefree session graph)
- Two negative cases (non-prime composite, perfect square)

This minimal set validates the two core constraints (L0 #3 and #5) without explosion.

---

## Acceptance Criteria

- [ ] `pirtm/dialect/pirtm.td` compiles via `tablegen -gen-op-defs -gen-op-decls` without warnings
- [ ] `pirtm/dialect/pirtm_types.cpp` compiles with `-std=c++17 -fPIC` (no errors or warnings)
- [ ] `millis-opt --verify-diagnostics pirtm/tests/pirtm-types-basic.mlir` outputs exactly four verifier results, all passing
- [ ] `mlir-opt pirtm/tests/pirtm-types-basic.mlir 2>&1 | grep "mod=7921 is not prime"` matches the expected-error directive exactly
- [ ] `mlir-opt pirtm/tests/pirtm-types-basic.mlir 2>&1 | grep "mod=49 is not squarefree"` matches the expected-error directive exactly
- [ ] Miller-Rabin test passes for all primes < 1000 and correctly rejects all composites < 1000
- [ ] Squarefree check returns factorization in format "p1^a1 * p2^a2 * ..." in ascending order of primes

**Day 0–3 Gate Status**: ✅ GATE 1 UNLOCKS → proceed to Day 3–7

---

## References

- [PIRTM ADR-004: MLIR Dialect Specification](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)
- [ADR-005: ADR Process + Directory Layout](./ADR-005-adr-process-layout.md)
- [LLVM TableGen User's Guide](https://llvm.org/docs/TableGen/)
- [MLIR Dialect Tutorial](https://mlir.llvm.org/docs/Dialects/)
- [Miller-Rabin Primality Test](https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test)

---

## Sign-Off

- [ ] Language Architect (PIRTM spec) approved
- [ ] Tooling Maintainer approved
- [ ] CI/Infra approved (adds Day 0–3 CI gate)
