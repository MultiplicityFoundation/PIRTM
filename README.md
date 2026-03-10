# PIRTM — Prime-Indexed Recursive Tensor Mathematics

**A verified contractive recurrence runtime with a compile-time MLIR dialect.**

PIRTM is the L0 (core-foundations) layer of the Tooling workspace.  Every
session in the system must be *proven contractive* before it executes.
Contractivity is verified in two temporal phases:

- **Transpile-time** (`contractivity-check`) — per-module, checked when
  `.pirtm.bc` bytecode is produced.
- **Link-time** (`spectral-small-gain`) — network-wide, checked when
  modules are linked into a session graph.

**Current status**: Phase 4 (LLVM + Standalone Runtime), 6 of 7 gates
passed (Day 90 performance benchmark in progress).

---

## Directory structure

```
pirtm/
├── __init__.py              Package root (version 0.4.1-phase2-mlir)
├── backend/                 TensorBackend protocol + NumPy reference impl
├── bindings/                Python ↔ native bindings layer
├── channels/                Communication primitives (shim.py)
├── core/                    Recurrence loop, projection, gain, certify
├── dialect/                 pirtm_types.py — Miller-Rabin + squarefree checks
├── examples/                Four JSON descriptor test cases
├── integrations/            GAP (Computer Algebra System) integration
├── mlir/                    Verification pass, LLVM codegen, dialect reference
├── spectral/                Operator identification & complex resonance (AAA)
├── src/runtime/             C++ standalone runtime (CMake, Phase 4)
├── tests/                   Test suite (27+ files)
├── tools/                   pirtm_inspect, grep_gates utilities
├── transpiler/              MLIR emitter, bytecode, linker, CLI
└── type_inference/          Type inference helpers
```

### docs/

```
docs/
├── adr/                     Architecture Decision Records (ADR-004 … ADR-009)
├── formats/                 Binary format specifications (.pirtm.bc, IANA)
├── migration/               prime-to-mod-rename guide
├── PIRTM_LIBERATION_ROADMAP.md
├── PHASE_{1..4}_EXPANDED.md
└── IMPLEMENTATION-DAYS-0-16-COMPLETE.md
```

---

## Quick start

```bash
# From the workspace root
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Run the PIRTM test suite
pytest pirtm/tests/ -v

# Inspect a compiled bytecode file
python -m pirtm.tools.pirtm_inspect pirtm/tests/fixtures/basic.pirtm.bc

# Transpile a descriptor to MLIR
pirtm transpile --input pirtm/examples/basic_contractive_system.json \
                --output mlir --epsilon 0.05
```

---

## CLI

| Command | Description |
|---------|-------------|
| `pirtm transpile --input <file> --output mlir` | Emit `.pirtm.bc` with contractivity proof |
| `pirtm transpile --input <file> --output numpy` | NumPy reference execution |
| `pirtm inspect <file.pirtm.bc>` | Print module report |
| `pirtm inspect --meta <file.pirtm.bc>` | Print contractivity metadata |
| `pirtm inspect --verify <file.pirtm.bc>` | Verify contractivity status |

Every `pirtm inspect` report includes the mandatory audit-chain line:

```
Audit Chain: NOT EMBEDDED — retrieve via pirtm audit <trace.log>
```

---

## Architecture

### Core recurrence (pirtm/core/)

The fundamental recurrence relation:

```
X_{t+1} = P( Ξ_t X_t  +  Λ_t T(X_t)  +  G_t )
```

| Symbol | Role |
|--------|------|
| `P`    | Projection (clip to `[-1, 1]`) |
| `Ξ_t` | Linear operator (identity or general) |
| `Λ_t` | Aggregation operator |
| `T`   | Nonlinear transformation (default: sigmoid) |
| `G_t` | External growth / guidance term |

Key modules:

| Module | Entry points |
|--------|-------------|
| `core/recurrence.py` | `step()`, `iterate()` |
| `core/certify.py` | `ContractivityCertificate`, `certify_state()`, `verify_trajectory()` |
| `core/projection.py` | `project()` |
| `core/gain.py` | `compute_spectral_radius()` |
| `core/executor.py` | `PirtmExecutor`, `ExecutionResult` |

### Backend abstraction (pirtm/backend/)

All core modules route through a `TensorBackend` protocol.  The NumPy
implementation (`numpy_backend.py`) is the default reference.  MLIR, LLVM,
and GPU backends can be registered without touching business logic.

```python
from pirtm.backend import get_backend, set_default_backend

backend = get_backend("numpy")   # default
set_default_backend("mlir")      # switch globally
```

### Dialect type system (pirtm/dialect/)

PIRTM introduces four MLIR types.  All `mod=` constraints are verified at
construction time:

| Type | Constraint | Enforced by |
|------|-----------|-------------|
| `!pirtm.cert(mod=p)` | `p` must be prime | Miller-Rabin |
| `!pirtm.epsilon(mod=p, value=ε)` | `p` prime, `0 < ε < 1` | Miller-Rabin |
| `!pirtm.op_norm_t(mod=p, norm=n)` | `p` prime, `n ≥ 0` | Miller-Rabin |
| `!pirtm.session_graph(mod=N, coupling=…)` | `N` squarefree | Trial division to √N |

Error messages include the factored form, e.g.:

```
mod=7921 is not prime (89^2)
mod=49 is not prime (7^2)
```

### Transpiler (pirtm/transpiler/)

| Module | Role |
|--------|------|
| `mlir_emitter_canonical.py` | Canonical MLIR emission with `mod=` syntax |
| `pirtm_bytecode.py` | `.pirtm.bc` serialization — carries `prime_index`, `ε`, `op_norm_T`, `proof_hash` in a non-allocating `!pirtm_proof` section |
| `pirtm_link.py` | Three-pass linker: name-resolution → commitment-crosscheck → matrix-construction → `spectral-small-gain` |
| `pirtm_perf.py` | Sparse-accelerated spectral radius (19× over dense NumPy on 512-dim) |
| `pirtm_predict.py` | Predictive margin warnings |
| `pirtm_reorder.py` | Margin-driven module reordering |
| `cli.py` | `pirtm` command-line entry point |

The linker rejects duplicate `identity_commitment` values with:

```
error: duplicate identity_commitment
```

### Spectral analysis (pirtm/spectral/)

| Module | Purpose |
|--------|---------|
| `laplacian.py` | Prime-Cayley Laplacian construction |
| `aaa.py` | AAA rational approximation |
| `continuation.py` | Complex resonance detection via analytic continuation |
| `fingerprint.py` | Operator identification via 5-point spectral shape test |

### C++ standalone runtime (pirtm/src/runtime/)

Phase 4 provides a CMake-built native library (`libpirtm_runtime`) that
exposes the recurrence loop as compiled machine code.  Python bindings are in
`pirtm/bindings/`.  The runtime targets ≥10× NumPy throughput on 512-dim
tensors (Day 90 gate).

---

## L0 invariants

These constraints are non-negotiable.  Code that violates any of them will be
rejected.

| # | Invariant |
|---|-----------|
| 1 | `pirtm.module` carries exactly one `prime_index`, one `epsilon`, one `op_norm_T`.  No `epsilon_map`.  No multi-prime modules. |
| 2 | `contractivity-check` runs at transpile time.  `spectral-small-gain` runs at link time.  No pass runs out of this order. |
| 3 | `!pirtm.cert` is always prime-typed.  There is no composite cert. |
| 4 | `pirtm.session_graph.gain_matrix` is never a transpile-time attribute — it must be `#pirtm.unresolved_coupling` until link time. |
| 5 | Composite `mod=` values must be squarefree (μ(mod) ≠ 0).  Atomic types require Miller-Rabin prime. |
| 6 | Human names in `coupling.json` do not survive into IR.  `pirtm.session_graph` is indexed by `prime_index` only. |
| 7 | `pirtm inspect` output must always include `Audit Chain: NOT EMBEDDED — retrieve via pirtm audit <trace.log>`. |

---

## Sequencing gates

Work proceeds in gate order.  A later gate must not begin before an earlier
one has a passing test.

| Gate | Day window | Requirement | Status |
|------|-----------|-------------|--------|
| 1 | 0–3 | `mlir-opt --verify-diagnostics pirtm-types-basic.mlir` passes all four lines | ✅ PASS |
| 2 | 3–7 | Coprime merge passes; non-coprime emits specified diagnostic | ✅ PASS |
| 3 | 7–14 | All `examples/` round-trip via `mlir_emitter.py --output mlir` | ✅ PASS |
| 4 | 14 | `pirtm inspect basic.pirtm.bc \| grep "contractivity_check: PASS"` | ✅ PASS |
| 5 | 14–16 | Commitment-collision test passes | ✅ PASS |
| 6 | 30 | `r=0.7` link passes; `r=1.1` link fails with spectral radius printed | ✅ PASS |
| 7 | 90 | `pirtm.step` ≥10× NumPy on 512-dim tensor | 🔄 In progress |

---

## Examples

```
pirtm/examples/
├── basic_contractive_system.json    prime_index=7919, ε=0.05, op_norm_T=0.9
├── composite_modulus_system.json    squarefree modulus example
├── multimodule_network.json         two coprime modules (7919 & 8191)
└── tightly_coupled_system.json      high-coupling stress test
```

Run all examples through the round-trip validator:

```bash
pytest pirtm/tests/test_day_7_14_round_trip.py -v
```

---

## Tests

```
pirtm/tests/
├── fixtures/            .pirtm.bc files + fixture generator
├── pirtm-types-basic.mlir          Day 0-3 MLIR diagnostic test
├── mlir_diagnostic_verifier.py     Python-based MLIR diagnostic simulator
├── test_dialect_types.py           Type-layer unit tests
├── test_day_3_7_coprime_merge.py   Coprime merge + grep gates
├── test_day_7_14_round_trip.py     Transpiler round-trip
├── test_day_14_contractivity.py    Bytecode + inspection
├── test_commitment_collision.py    Duplicate identity_commitment (Day 14-16)
├── test_spectral_gates.py          Network stability: r=0.7 / r=1.1
├── test_phase4_integration.py      End-to-end Phase 4
├── test_predictive_warnings.py     Margin prediction
├── test_module_reordering.py       Margin-driven reordering
└── ...
```

Run the full PIRTM test suite:

```bash
pytest pirtm/tests/ -v
```

---

## ADRs

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-004](docs/adr/ADR-004.md) | PIRTM MLIR Dialect (canonical spec, lives in PIRTM repo) | Spec |
| [ADR-005](docs/adr/ADR-005-adr-process-layout.md) | ADR Process Layout | Accepted |
| [ADR-006](docs/adr/ADR-006-dialect-type-layer-gate.md) | Dialect Type-Layer Gate (Day 0–3) | ✅ Implemented |
| [ADR-007](docs/adr/ADR-007-prime-mod-migration.md) | Prime → Mod Migration | 🔄 Active |
| [ADR-008](docs/adr/ADR-008-linker-coupling-gates.md) | Linker + Coupling Gates | 🔄 Active |
| [ADR-009](docs/adr/ADR-009-digital-vin-and-glass-box-identity.md) | Digital VIN + Glass-Box Identity | 🔄 Active |

ADR-004 is the canonical source of truth for all type-system and
contractivity-semantics decisions.  Tooling ADRs implement it and may not
redefine its semantics.

---

## Relation to the workspace

PIRTM is L0 in the Tooling layered architecture:

```
L5 Applications
L4 ZK Proof & Verification
L3 Domain Reasoning
L2 Formal Methods
L1 Sigma Kernel
L0 Core Foundations  ← pirtm/ lives here
```

See the [workspace README](../README.md) for the full layer description.
