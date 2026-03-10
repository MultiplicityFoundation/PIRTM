# PIRTM Liberation Roadmap: From NumPy Substrate to Standalone Runtime

**Status**: Planning Phase  
**Last Updated**: 2026-03-08  
**Document Authority**: Prime-Indexed Recursive Tensor Mathematics Core Team

---

## Executive Summary

This document outlines the **4-phase liberation strategy** to transform PIRTM from a NumPy-dependent library into a **certified standalone runtime** with MLIR backend support, compile-time contractivity guarantees, and cross-platform hardware reach.

**Central Tension**: NumPy provides speed-to-prototype and ecosystem reach, but encodes the L0 invariant (`q_t < 1 - ε`) as *runtime assertions* rather than *compile-time guarantees*. Each day spent in the NumPy substrate accumulates technical debt against the promise of verifiable computation.

**Strategic Decision**: Rather than a clean break (which forfeits Python interop), PIRTM will use an **adapter + liberation pattern** — NumPy remains the default reference implementation, but the core `recurrence`, `projection`, `gain`, and `certify` modules route through a `TensorBackend` protocol that enables MLIR, Rust, and GPU backends to coexist without touching business logic.

---

## Four Levers & Timelines

| Lever | Horizon | Owner | Metric | Impact |
|-------|---------|-------|--------|--------|
| **L1: Backend Abstraction** | 7 days | Core Library | Zero direct `import numpy` in core modules | Unblock MLIR/Rust backends |
| **L2: MLIR Emission** | 30 days | Transpiler Team | `pirtm transpile --output mlir` emits verifiable linalg dialect code | Enable compile-time verification |
| **L3: Type System Enforcement** | 60 days | Type System Lead | Contractivity bounds as first-class type attributes | Shift from runtime checks to static guarantees |
| **L4: Standalone Runtime** | 120 days | Runtime Engineering | PIRTM VM or LLVM backend ships independently; NumPy optional | True liberation |

---

## Phase 1: Backend Abstraction (Days 0–7)

### Objective
Decouple all business logic from the NumPy implementation via a `TensorBackend` protocol.

### Artifacts

**1.1 – ADR-006: Backend Abstraction Protocol**
- **File**: `docs/adr/ADR-006-backend-abstraction.md`
- **References**: ADR-004 (type layer), ADR-001 (Day 0–3 gates)
- **Scope**: Define `TensorBackend` protocol, specify implementation contract, document adapter registration
- **Decision**: NumPy remains default; MLIR/Rust/GPU backends slot in via protocol without touching core logic

**1.2 – Core Backend Module**
- **File**: `src/pirtm/backend/__init__.py` (220 lines)
- **Exports**:
  ```python
  class TensorBackend(Protocol):
      """Specification for tensor computation backends."""
      def matmul(self, A: Array, x: Array) -> Array: ...
      def add(self, x: Array, y: Array) -> Array: ...
      def multiply(self, x: Array, y: Array) -> Array: ...
      def norm(self, x: Array) -> Scalar: ...
      def eye(self, n: int) -> Array: ...
      def zeros(self, shape: tuple) -> Array: ...
      def ones(self, shape: tuple) -> Array: ...
      def clip(self, x: Array, min_val: float, max_val: float) -> Array: ...
      def sqrt(self, x: Array) -> Array: ...
      def exp(self, x: Array) -> Array: ...
      def log(self, x: Array) -> Array: ...
  
  def get_backend(name: str = "numpy") -> TensorBackend: ...
  def set_default_backend(name: str) -> None: ...
  ```

**1.3 – NumPy Backend Implementation**
- **File**: `src/pirtm/backend/numpy_backend.py` (150 lines)
- **Status**: Default reference implementation
- **Wraps**: All NumPy operations into protocol-compliant methods

**1.4 – Core Module Refactoring**
- **Files affected**:
  - `src/pirtm/recurrence.py`: Remove `import numpy`; use `backend.matmul()`, `backend.norm()`
  - `src/pirtm/projection.py`: Use `backend.clip()`, `backend.multiply()`
  - `src/pirtm/gain.py`: Use `backend.eye()`, `backend.ones()`
  - `src/pirtm/certify.py`: Use `backend.norm()`, `backend.clip()` for validation
- **Test coverage**: Verify all refactored modules work with NumPy backend; add parameterized tests for future backends

### Deliverables

| Artifact | Lines | Status | Rationale |
|----------|-------|--------|-----------|
| ADR-006 | ~40 | Draft | Specification document |
| Backend protocol | 220 | Code | Core abstraction |
| NumPy backend | 150 | Code | Reference impl |
| Refactored modules | ~500 | Code | Core logic no longer NumPy-coupled |
| Parameterized tests | ~200 | Code | Verify backend contract |

### Success Criteria
✅ `pytest src/pirtm/tests/` passes with NumPy backend  
✅ Zero direct `import numpy` in `recurrence.py`, `projection.py`, `gain.py`, `certify.py`  
✅ `get_backend("numpy")` instantiates and executes recurrence loop  

---

## Phase 2: MLIR Emission from Transpiler (Days 8–37)

### Objective
Emit verifiable MLIR `linalg` dialect code from the recurrence loop, with contractivity bounds as first-class attributes.

### Background
The existing `transpiler` directory already handles:
- `computation` and `data_asset` descriptors with `--prime-index`, `--identity-commitment` flags
- Dual-hash witnesses (SHA256 + Poseidon-compatible)
- CSL emission gating via `EmissionPolicy`

Phase 2 extends this to **lower the recurrence loop to MLIR** with contractivity provenance.

### Artifacts

**2.1 – ADR-007: MLIR Lowering Pipeline**
- **File**: `docs/adr/ADR-007-mlir-lowering.md`
- **References**: ADR-006 (backend protocol), ADR-004 (contractivity semantics)
- **Scope**: IR design for `pirtm.linalg` dialect, verification attributes, witness encoding
- **Decision**: Emit std + linalg dialects; attach contractivity bounds as metadata attributes

**2.2 – MLIR Lowering Module**
- **File**: `src/pirtm/transpiler/mlir_lowering.py` (400 lines)
- **Key classes**:
  ```python
  class MLIREmitter:
      """Lower recurrence loop to MLIR."""
      def emit_recurrence(self, policy: CarryForwardPolicy, 
                         kernel: FullAsymmetricAttributionKernel,
                         num_steps: int) -> MLIRModule: ...
      
      def emit_contractivity_bounds(self, epsilon: float, 
                                   confidence: float) -> List[Attribute]: ...
      
      def emit_witness(self, iss_bound: float, 
                      ace_cert: ACECertificate) -> Attribute: ...
  
  class ContractivityAttribute(Attribute):
      """First-class contractivity bound metdata."""
      epsilon: float
      confidence: float
      ace_certificate: str  # Encoded as witness hash
  ```

**2.3 – Transpiler CLI Extension**
- **File**: `src/pirtm/transpiler/cli.py` (additions)
- **New flags**:
  ```bash
  pirtm transpile --input descriptor.yaml \
    --output mlir \
    --mlir-dialect linalg \
    --emit-contractivity \
    --witness-format poseidon
  ```
- **Output**: `.mlir` file with embedded contractivity metadata

**2.4 – MLIR Verifier Tests**
- **File**: `src/pirtm/tests/test_mlir_verification.py` (300 lines)
- **Test scenarios**:
  - Recurrence loop round-trips to MLIR and back
  - Contractivity bounds are correctly encoded as attributes
  - Witnesses match expected Poseidon hashes
  - `mlir-opt --verify-diagnostics` passes on generated code

### Deliverables

| Artifact | Lines | Status | Rationale |
|----------|-------|--------|-----------|
| ADR-007 | ~50 | Draft | MLIR design spec |
| MLIREmitter | 400 | Code | Core lowering logic |
| CLI extension | 80 | Code | User-facing transpiler command |
| Verification tests | 300 | Code | Round-trip + witness validation |
| Documentation | ~60 | Docs | MLIR dialect reference |

### Success Criteria
✅ `pirtm transpile --output mlir` produces valid MLIR that parses with `mlir-opt`  
✅ Contractivity bounds appear as attributes in the emitted code  
✅ Witness hashes match expected Poseidon commitments  
✅ `mlir-opt --verify-diagnostics` passes (no unverified operations)  

---

## Phase 3: Type System Enforcement (Days 38–97)

### Objective
Shift contractivity validation from runtime assertions to compile-time type attributes.

### Key Insight
Phase 2 emits contractivity as *metadata*, but the type system doesn't yet *enforce* it. Phase 3 introduces a **contractivity type** that the compiler can reason about:

```mlir
!pirtm.contractivity<epsilon = 0.1, confidence = 0.9999>
```

Operations on `contractivity`-typed values are subject to contraction laws baked into the type system itself.

### Artifacts

**3.1 – ADR-008: Contractivity Type System**
- **File**: `docs/adr/ADR-008-contractivity-types.md`
- **References**: ADR-007 (MLIR lowering), ADR-004 (contractivity semantics)
- **Scope**: Type grammar, inference rules, verification obligations
- **Decision**: `!pirtm.contractivity` is a dialect type; operations on contractivity-typed values check Lipschitz bounds at definition time

**3.2 – MLIR Dialect Definition**
- **File**: `src/pirtm/mlir/pirtm_dialect.td` (350 lines)
- **Defines**:
  - `pirtm.contractivity<epsilon, confidence>` type
  - `pirtm.certify` operation (produces contractivity-typed output)
  - `pirtm.recurrence` operation (consumes contractivity-typed loop variable)
  - Type constraints and verification predicates

**3.3 – Type Inference Engine**
- **File**: `src/pirtm/type_inference/contractivity_inference.py` (280 lines)
- **Algorithm**: Walk the computation graph; propagate contractivity bounds via Lipschitz composition
  ```
  If T₁ : contractivity<ε₁> and T₂ : contractivity<ε₂>
    Then (T₁ ∘ T₂) : contractivity<min(ε₁, ε₂)>
  ```
- **Integration**: Runs as a pass in the lowering pipeline (Phase 2)

**3.4 – Verification Pass**
- **File**: `src/pirtm/mlir/passes/verify_contractivity.cc` (220 lines, C++)
- **LLVM pass** that checks:
  - All `pirtm.recurrence` operations have contractivity-typed inputs
  - Lipschitz bounds are computed soundly
  - ACE certificates are present and valid
  - CSL emission gates respect contractivity contracts

**3.5 – Comprehensive Type Tests**
- **File**: `src/pirtm/tests/test_contractivity_types.py` (400 lines)
- **Test coverage**:
  - Type inference on synthetic computation graphs
  - Contraction law verification (composition, amplification, etc.)
  - False positives/negatives detection (what *should* fail type check?)
  - Round-trip: Python → MLIR → verification → inference

### Deliverables

| Artifact | Lines | Status | Rationale |
|----------|-------|--------|-----------|
| ADR-008 | ~60 | Draft | Type system spec |
| MLIR dialect def | 350 | Code | Type grammar + ops |
| Type inference | 280 | Code | Lipschitz propagation |
| Verification pass | 220 | Code (C++) | Compiler integration |
| Type tests | 400 | Code | Verification coverage |

### Success Criteria
✅ Type inference correctly propagates contractivity bounds through composition  
✅ `mlir-opt -verify-pirtm-contractivity` rejects uncontractivity programs  
✅ All Phase 2 generated MLIR passes type verification  
✅ Inference time is < 100ms for graphs with 1000+ operations  

---

## Phase 4: Standalone Runtime (Days 98–127)

### Objective
Build a PIRTM VM or LLVM-compiled backend that executes recurrence loops without NumPy.

### Decision Point: VM vs. LLVM Backend

| Dimension | PIRTM VM | LLVM Backend |
|-----------|----------|--------------|
| **Time to MVP** | 30 days | 45 days |
| **Verification depth** | Can embed witness checks in bytecode | Compile-time only |
| **Runtime overhead** | Interpreter (10–20× NumPy) | Native (1–5× NumPy) |
| **Debug ergonomics** | Excellent (step through bytecode) | Requires LLDB integration |
| **Hardware reach** | CPU only | CPU + GPU (via LLVM) |

**Recommendation**: Start with **LLVM backend** for performance-critical workloads; add VM later for debugging/verification workflows.

### Artifacts

**4.1 – ADR-009: LLVM Compilation for PIRTM**
- **File**: `docs/adr/ADR-009-llvm-compilation.md`
- **References**: ADR-008 (type system), ADR-007 (MLIR lowering)
- **Scope**: LLVM code generation from MLIR, ACE witness embedding, runtime linking
- **Decision**: Use `mlir-to-llvm` conversion; embed witness validation as preamble; link against `libpirtm-runtime.so`

**4.2 – LLVM Code Generation**
- **File**: `src/pirtm/mlir/llvm_codegen.py` (300 lines)
- **Pipeline**:
  1. Convert `pirtm` dialect to `std` + `linalg`
  2. Lower `linalg` to `affine` loops
  3. Raise `affine` to `llvm` dialect
  4. Export to `.ll` (human-readable LLVM IR)
  5. Compile to `.so` with `llc`

**4.3 – Runtime Library**
- **File**: `src/pirtm/runtime/libpirtm_runtime.cpp` (400 lines, C++)
- **Exports**:
  ```c
  struct pirtm_state {
      double* X;        // State vector
      double* witness;  // ACE certificate
      int n;            // Dimension
      float epsilon;    // Contractivity bound
  };
  
  int pirtm_init(pirtm_state* state, int n, float epsilon);
  int pirtm_step(pirtm_state* state);
  int pirtm_verify_witness(pirtm_state* state, const char* expected_hash);
  void pirtm_free(pirtm_state* state);
  ```

**4.4 – Python Bindings**
- **File**: `src/pirtm/bindings/pirtm_runtime.pyi` + `src/pirtm/bindings/pirtm_runtime_impl.cpp` (200 lines)
- **Purpose**: Call compiled LLVM code from Python, fallback to NumPy if needed
- **Key function**:
  ```python
  def run_compiled(descriptor: Dict, steps: int, backend: str = "llvm") -> Dict:
      """Execute with LLVM backend; return to NumPy for post-processing."""
      ...
  ```

**4.5 – Multi-Backend Harness**
- **File**: `src/pirtm/core/executor.py` (250 lines)
- **Unified interface**:
  ```python
  executor = PirtmExecutor(backend="llvm")  # or "numpy", "mlir"
  result = executor.run(policy, kernel, steps=100)
  ```
- **Auto-fallback**: If LLVM compilation fails, silently drop to NumPy

**4.6 – Standalone Distribution**
- **File**: `setup.py` (extended) + `pyproject.toml` + `MANIFEST.in`
- **Build system**: Detect LLVM install; compile runtime; package `.so` in wheel
- **Installation**: `pip install pirtm[llvm]` downloads pre-built LLVM runtime; `pip install pirtm` uses NumPy fallback
- **CI/CD**: Multi-platform builds (Linux x86_64, arm64; macOS; Windows via MSVC)

**4.7 – Comprehensive Integration Tests**
- **File**: `src/pirtm/tests/test_multi_backend_executor.py` (500 lines)
- **Scenarios**:
  - LLVM backend produces same results as NumPy (within float epsilon)
  - Witness validation works in compiled code
  - Fallback to NumPy on compilation error
  - Performance benchmarks (NumPy vs. LLVM)
  - Cross-platform: Linux, macOS, Windows

### Deliverables

| Artifact | Lines | LOC | Status | Rationale |
|----------|-------|-----|--------|-----------|
| ADR-009 | ~50 | Docs | Draft | LLVM design spec |
| LLVM codegen | 300 | Python | Code | MLIR → LLVM conversion |
| Runtime library | 400 | C++ | Code | Core execution engine |
| Python bindings | 200 | C++ | Code | Bridge to Python |
| Executor harness | 250 | Python | Code | Unified backend interface |
| Packaging | 100 | Config | Code | Wheel + platform support |
| Integration tests | 500 | Python | Code | Multi-backend verification |

### Success Criteria
✅ `pirtm.core.executor.PirtmExecutor(backend="llvm")` runs without error  
✅ LLVM backend produces outputs identical to NumPy (max 1e-10 difference)  
✅ Witness validation passes in compiled code  
✅ LLVM backend is 5–10× faster than NumPy on 1000-dim recurrence  
✅ Wheel installs cleanly on Ubuntu 22.04, macOS 13+, Windows 11  
✅ `pip install pirtm[llvm]` works without requiring manual LLVM installation  

---

## Cross-Phase Considerations

### ADR Governance

| ADR | Title | Scope | Links |
|-----|-------|-------|-------|
| ADR-004 | Type-layer specification | Cantitative semantics, mod invariant, contractivity bounds | **Normative spec** |
| ADR-006 | Backend abstraction | Protocol design, adapter registration | Phase 1 |
| ADR-007 | MLIR lowering | IR design, witness encoding, verification | Phase 2 |
| ADR-008 | Contractivity types | MLIR dialect, type inference, verification pass | Phase 3 |
| ADR-009 | LLVM compilation | Code generation, runtime library, packaging | Phase 4 |

**Rule**: ADR-004 is **read-only**. Phases 1–4 ADRs must cite ADR-004 without redefining semantics.

### Testing Strategy

**Phase-gated testing**:
- **Phase 1 exit gate**: All NumPy tests pass; no direct `import numpy` in core modules
- **Phase 2 exit gate**: MLIR emits valid `linalg` dialect; `mlir-opt --verify-diagnostics` passes
- **Phase 3 exit gate**: Type inference runs in < 100ms; verification pass rejects non-contractivity programs
- **Phase 4 exit gate**: LLVM and NumPy backends produce identical outputs; performance > 5×

### Timeline & Resource Allocation

| Phase | Duration | Parallel Work | Critical Path |
|-------|----------|---------------|----------------|
| **P1** | 7 days | DX polish (docs, error msgs) | Backend protocol design |
| **P2** | 30 days | Update ADR-004 examples | MLIR lowering + transpiler |
| **P3** | 60 days | Educational materials | Type inference engine |
| **P4** | 30 days | Distribution packaging | LLVM codegen + bindings |

**Total critical path**: ~130 days (~19 weeks) from today (March 8, 2026) → **early June 2026**.

**Parallel workstreams** can begin immediately:
- P1 backend abstraction (independent of other phases)
- Updating ADR-004 documentation (can run alongside P1–P4)
- Building CI/CD infrastructure for multi-platform builds (ahead of P4)

---

## Success Metrics & KPIs

### Technical Metrics

| KPI | Target | Phase | Measurable |
|-----|--------|-------|-----------|
| Core modules decoupled from NumPy | 100% | P1 | 0 direct `import numpy` in core 4 files |
| MLIR parse success rate | 100% | P2 | `mlir-opt` verifies all emitted code |
| Type inference coverage | 95% | P3 | Inference engine handles 95% of real graphs |
| Backend performance parity | 5–10× | P4 | LLVM faster than NumPy on 1000-dim recurrence |
| Cross-platform build success | 100% | P4 | Wheels build + install on Linux, macOS, Windows |

### Adoption Metrics

| KPI | Target | Phase | Measurable |
|-----|--------|-------|-----------|
| Users running LLVM backend | > 50% | P4+30d | GitHub issues, telemetry |
| Documentation completeness | 90% | P4 | Public AD Rs + examples + migration guide |
| Community PRs for backends | > 2 | P4+60d | GPU, TPU, FPGA backends from community |

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| LLVM compilation adds complexity | High | Start with simple graphs; use fallback strategy |
| Type inference becomes intractable (exponential cases) | Medium | Use heuristic inference + user annotations |
| Windows LLVM toolchain unavailable | Medium | Pre-compile `libpirtm_runtime.dll`; include in wheel |
| Existing NumPy API breaks during refactoring | High | Maintain 100% backward-compat shim; deprecation window |

---

## Deliverables Summary

### By Phase

**Phase 1**: 1 ADR + 4 code modules + tests  
**Phase 2**: 1 ADR + 2 code modules + tests + docs  
**Phase 3**: 1 ADR + 2 code modules + 1 C++ pass + tests  
**Phase 4**: 1 ADR + 4 code modules + C++ runtime + wheel + tests  

**Total**: 4 ADRs + ~2500 LOC (Python) + ~620 LOC (C++) + comprehensive tests

---

## Next Steps

1. **Approve this roadmap** with core team (governance)
2. **Assign owners** to each phase (resource planning)
3. **Create Phase 1 ADR-006** (backend abstraction spec)
4. **Kick off Phase 1** backend protocol design (7-day sprint)
5. **Parallel**: Update ADR-004 documentation with examples from Phase 1–4

**First checkpoint**: April 15, 2026 (Phase 1 complete)

---

## Appendix: Relation to Multiplicity Phase 1–2

The concurrent **Multiplicity attribution kernel & ledger project** (Phase 1–2, completed) informs several P IRTMliberation decisions:

| Multiplicity Achievement | PIRTM Application |
|--------------------------|-------------------|
| Backend adapter pattern (LedgerAwareGraphBackend, LedgerAwareSpectralBackend) | Model for PIRTM `TensorBackend` protocol (P1) |
| FullAsymmetricAttributionKernel (5 kernel types via enum) | Inspect kernel strategies for contractivity bounds (P3) |
| FullHealthMonitor + FullLedgerAudit | Observability pattern for LLVM runtime (P4) |
| Comprehensive testing (55/55 tests Phase 1 + 100+ Phase 2) | Testing rigor for multi-backend executor (P4) |
| CLIintegration (--ledger-aware flag, config JSON/YAML) | Model for Phase 4 `pirtm` CLI with `--backend` flag |

**Learning from Multiplicity**: The modular test-first approach and clean separation of concerns (Phase 1 core → Phase 2 extensions) directly informed this roadmap's ADR governance and phased delivery.

