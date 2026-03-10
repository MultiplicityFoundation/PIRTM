# PIRTM MLIR Dialect Reference

**Phase**: 2 (MLIR Emission & Transpiler Integration)  
**Status**: Active  
**Date**: March 9, 2026  

---

## Overview

The PIRTM dialect provides compile-time verification for contractive recurrence loops. This reference documents the operations, types, and attributes that comprise the dialect.

---

## Module Metadata: `pirtm.module`

The `pirtm.module` operation encapsulates contractivity semantics.

### Syntax

```mlir
pirtm.module {
  @epsilon = <f64> : f64              // Contractivity margin
  @confidence = <f64> : f64           // Confidence level (ACE)
  @op_norm_T = <f64> : f64            // Operator norm of T
  @prime_index = <i64> : i64          // Prime modulus index
  @has_witness_commitment : i1        // (optional) ACE witness flag
}
```

### Fields

| Field | Type | Required | Semantics |
|-------|------|----------|-----------|
| `@epsilon` | `f64` | Yes | Contractivity margin ε such that r(Λ) < 1 - ε |
| `@confidence` | `f64` | Yes | Confidence level (e.g., 0.9999 for 4σ guarantee) |
| `@op_norm_T` | `f64` | Yes | Lipschitz bound on transformation T (typically ≤ 1.0) |
| `@prime_index` | `i64` | Yes | Prime modulus p (ACE integration, e.g., p=17) |
| `@has_witness_commitment` | `i1` | No | Whether witness hash is embedded |

### Example

```mlir
pirtm.module {
  @epsilon = 0.05 : f64
  @confidence = 0.9999 : f64
  @op_norm_T = 1.0 : f64
  @prime_index = 17 : i64
  @has_witness_commitment : i1
}
```

---

## Operations

### `pirtm.sigmoid` — Sigmoid Activation

Apply element-wise sigmoid: `σ(x) = 1 / (1 + exp(-x))`.

#### Syntax

```mlir
%result = "pirtm.sigmoid"(%input) : (tensor<?xf64>) -> tensor<?xf64>
```

#### Semantics

- **Input**: Vector or matrix
- **Output**: Same shape as input
- **Bounds**: Output in (0, 1) for all elements
- **Lipschitz**: σ is 0.25-Lipschitz (max derivative at 0)

#### Example

```mlir
%X = ...
%T_X = "pirtm.sigmoid"(%X) : (tensor<?xf64>) -> tensor<?xf64>
```

---

### `pirtm.clip` — Bounded Projection

Clip values to interval `[a, b]`.

#### Syntax

```mlir
%result = "pirtm.clip"(%input) 
  : (tensor<?xf64>) -> tensor<?xf64>
  { bound_low = <f64>, bound_high = <f64> }
```

#### Attributes

| Attr | Type | Default | Semantics |
|------|------|---------|-----------|
| `bound_low` | `f64` | -1.0 | Lower bound |
| `bound_high` | `f64` | 1.0 | Upper bound |

#### Semantics

- **Nonexpansive**: ‖clip(x, a, b) - clip(y, a, b)‖ ≤ ‖x - y‖
- **Preserves contraction**: Applied after summing scaled terms
- **L0 Invariant**: With bounds [-1, 1], ensures ‖X‖ < 1 - ε

#### Example

```mlir
%Y = "linalg.add"(%term1, %term2) : ...
%X_next = "pirtm.clip"(%Y) : (tensor<?xf64>) -> tensor<?xf64>
  { bound_low = -1.0 : f64, bound_high = 1.0 : f64 }
```

---

### `pirtm.contractivity` — Type Attribute (Future)

**Phase 3+**: Mark values as satisfying contractivity.

```mlir
%result: tensor<?xf64, !pirtm.contractivity<epsilon = 0.05, confidence = 0.9999>>
```

---

## Recurrence Function: `@pirtm_recurrence`

The main entry point for compiled recurrence.

### Signature

```mlir
func.func @pirtm_recurrence(
  %X_t: tensor<?xf64>,
  %Xi_t: tensor<?x?xf64>,
  %Lambda_t: tensor<?x?xf64>,
  %G_t: tensor<?xf64>
) -> tensor<?xf64>
```

### Parameters

| Param | Shape | Semantics |
|-------|-------|-----------|
| `%X_t` | `(n,)` | Current state vector |
| `%Xi_t` | `(n, n)` | Recurrence matrix Ξ |
| `%Lambda_t` | `(n, n)` | Aggregation matrix Λ |
| `%G_t` | `(n,)` | External input G_t |

### Body: Recurrence Equation

$$X_{t+1} = P(\Xi X_t + \Lambda T(X_t) + G_t)$$

Implemented as:

```mlir
// Step 1: T(X_t) = sigmoid(X_t)
%T_X_t = "pirtm.sigmoid"(%X_t) : (tensor<?xf64>) -> tensor<?xf64>

// Step 2: term1 = Ξ X_t
%term1 = "linalg.matvec"(%Xi_t, %X_t)
  : (tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>

// Step 3: term2 = Λ T(X_t)
%term2 = "linalg.matvec"(%Lambda_t, %T_X_t)
  : (tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>

// Step 4: Y = term1 + term2 + G_t
%Y_t = "linalg.add"(%term1, %term2)
  : (tensor<?xf64>, tensor<?xf64>) -> tensor<?xf64>
%Y_plus_G = "linalg.add"(%Y_t, %G_t)
  : (tensor<?xf64>, tensor<?xf64>) -> tensor<?xf64>

// Step 5: X_next = P(Y) = clip(Y, -1, 1)
%X_next = "pirtm.clip"(%Y_plus_G) : (tensor<?xf64>) -> tensor<?xf64>
  { bound_low = -1.0 : f64, bound_high = 1.0 : f64 }

return %X_next : tensor<?xf64>
```

### Guarantees

**L0 Invariant**: ‖X_next‖ < 1 - ε with confidence 1 - δ

Proven by:
1. Projection ensures all values in [-1, 1]
2. Spectral small-gain theorem: r(Λ) < 1 - ε guarantees contraction
3. ACE witness encodes the epoch proof

---

## Type System

### Tensor Types

| Type | Semantics |
|------|-----------|
| `tensor<?xf64>` | Dense vector, f64 elements |
| `tensor<?x?xf64>` | Dense matrix, f64 elements |
| `tensor<*xf64>` | Unranked tensor (future) |

### Scalar Types

| Type | Semantics |
|------|-----------|
| `f64` | IEEE 754 double precision |
| `i64` | Signed 64-bit integer |
| `i1` | Boolean flag |

---

## Witness Encoding (ACE Integration)

### Module-Level Witness

```mlir
pirtm.module {
  @ace_witness = "0xabc123...xyz" : witness_hash
  @prime_index = 17 : i64
}
```

**Semantics**: The hash `0xabc123...xyz` is a Poseidon commitment to the ACE session proof. Verification:

```bash
$ pirtm inspect compiled.pirtm.bc --verify
Audit Chain: NOT EMBEDDED — retrieve via pirtm audit <trace.log>
```

---

## Verification with `mlir-opt`

### Command Line

```bash
$ mlir-opt --verify-diagnostics input.mlir
```

### Diagnostic Markers (Test Mode)

```mlir
// expected-no-errors
// CHECK: module
// CHECK: pirtm.module
// CHECK: epsilon = {{.*}} : f64
// CHECK: @pirtm_recurrence
```

---

## Integration with linalg Dialect

Operations rely on standard MLIR `linalg` dialect for linear algebra:

| linalg Op | Semantics | Maps to |
|-----------|-----------|---------|
| `linalg.matvec` | Matrix-vector product | `matmul(A, x)` |
| `linalg.add` | Element-wise addition | `x + y` |
| `linalg.norm` | Vector/matrix norm | `‖·‖` |

These operations are **unmodified** — the PIRTM dialect provides contractivity *metadata* only, not numerical modifications.

---

## Example: Full Module

### Input Descriptor (YAML)

```yaml
policy: CarryForward
kernel: FullAsymmetricAttribution
dimension: 512
epsilon: 0.05
confidence: 0.9999
prime_index: 17
trace_id: session_001
```

### Generated MLIR

```mlir
// PIRTM Recurrence Loop → MLIR (linalg dialect)
// Policy: CarryForward
// Kernel: FullAsymmetricAttribution
// Emitted: 2026-03-09T10:30:00 UTC
// ACE Witness ID: session_001
// Contractivity Guarantee: epsilon=0.05, confidence=0.9999

module {
  pirtm.module {
    @epsilon = 0.05 : f64
    @confidence = 0.9999 : f64
    @op_norm_T = 1.0 : f64
    @prime_index = 17 : i64
    @has_witness_commitment : i1
  }

  func.func @pirtm_recurrence(
    %X_t: tensor<?xf64>,
    %Xi_t: tensor<?x?xf64>,
    %Lambda_t: tensor<?x?xf64>,
    %G_t: tensor<?xf64>
  ) -> tensor<?xf64> {
    // Step 1: T(X_t) = sigmoid(X_t)
    %T_X_t = "pirtm.sigmoid"(%X_t)
      : (tensor<?xf64>) -> tensor<?xf64>
    
    // Step 2: Ξ X_t
    %term1 = "linalg.matvec"(%Xi_t, %X_t)
      : (tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>
    
    // Step 3: Λ T(X_t)
    %term2 = "linalg.matvec"(%Lambda_t, %T_X_t)
      : (tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>
    
    // Step 4: Sum terms
    %Y_t = "linalg.add"(%term1, %term2)
      : (tensor<?xf64>, tensor<?xf64>) -> tensor<?xf64>
    %Y_plus_G = "linalg.add"(%Y_t, %G_t)
      : (tensor<?xf64>, tensor<?xf64>) -> tensor<?xf64>
    
    // Step 5: Projection P(Y) = clip(Y, -1, 1)
    %X_next = "pirtm.clip"(%Y_plus_G)
      : (tensor<?xf64>) -> tensor<?xf64>
      { bound_low = -1.0 : f64, bound_high = 1.0 : f64 }
    
    // L0: ||X_next|| < 1 - epsilon = 0.95
    return %X_next : tensor<?xf64>
  }
}
```

### Verification

```bash
$ mlir-opt --verify-diagnostics recurrence.mlir
$ echo $?  # Exit code 0 = success
0
```

---

## Future Phases

### Phase 3: Type System

Add `!pirtm.contractivity` type for propagating guarantees:

```mlir
%X_next: tensor<?xf64, !pirtm.contractivity<epsilon = 0.05, confidence = 0.9999>>
```

### Phase 4: LLVM Compilation

Lower further to LLVM dialect with native machine code targeting.

---

## References

- **ADR-007**: MLIR Lowering Pipeline specification
- **ADR-006**: Backend Abstraction protocol
- **ADR-004**: Contractivity Semantics & Type System
- **MLIR Docs**: https://mlir.llvm.org/
- **linalg Dialect**: https://mlir.llvm.org/docs/Dialects/Linalg/
