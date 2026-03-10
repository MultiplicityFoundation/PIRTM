# ADR-004: pirtm MLIR Dialect — Type System, Governance Architecture, and Two-Phase Compilation

**Status**: Accepted  
**Date**: 2026-03-08  
**Owner**: Language Architect  
**Supersedes**: None (first dialect ADR)  
**Blocks**: `mlir_emitter.py`, `pirtm_core/` Rust crate, `SpectralGovernor` refactor, `pirtm link` CLI, `pirtm inspect`

---

## Context

PIRTM's contractivity invariant — `q_t < 1 − ε` — is currently enforced at runtime via
`ace_certificate()`. The standalone runtime requires this invariant to be a compile-time
structural property. This ADR specifies the `pirtm` MLIR dialect that makes non-contractive
programs syntactically invalid, and the two-phase compilation model that maps PIRTM's two
mathematically distinct proof obligations onto the correct temporal horizons.

Four prior decisions are recorded here as locked (Phase Mirror sessions, 2026-03-08):

1. Prime indices are type parameters, not runtime attributes.
2. Composite types are squarefree — the CRT isomorphism is the governing invariant.
3. Session governance is flat: one `pirtm.module` per atomic prime channel. No `epsilon_map`. Ever.
4. Binary artifacts are self-describing: proof metadata is embedded offline-readable; audit chain is runtime-only.

---

## Decision

### 1. Type System — Two-Tier ChannelKind Hierarchy

All channel identity is carried in a `mod=` parameter (not `prime=`). The word `prime=` is
retired across the entire dialect and Python data model. `prime_index` as a named attribute
on `pirtm.module` keeps its name — only type parameters on tensor types become `mod=`.

| Type | Mnemonic | `mod=` constraint | Verifier pass |
|---|---|---|---|
| `AtomicTensorType` | `!pirtm.tensor` | Miller-Rabin prime | `prime-validity` |
| `CompositeTensorType` | `!pirtm.ctensor` | squarefree — μ(mod) ≠ 0 | `squarefree-validity` |
| `CertType` | `!pirtm.cert` | Miller-Rabin prime (always atomic) | `prime-validity` |
| `CertPairType` | `!pirtm.cert_pair` | squarefree; factors match input certs | `squarefree-validity` |

`CertType` is strictly prime-typed. There is no composite cert. `CertPairType` is the
categorical product of two prime certs, produced by `pirtm.merge_cert`.

**TableGen stubs (Day 0–3 gate):**

```tablegen
// pirtm.td
def AtomicTensorType : PirtmType<"AtomicTensor", "tensor"> {
  let parameters = (ins "int64_t":$dim, "Type":$dtype, "int64_t":$mod);
  let genVerifyDecl = 1;
  // verifyConstructionInvariants: Miller-Rabin(mod)
}

def CompositeTensorType : PirtmType<"CompositeTensor", "ctensor"> {
  let parameters = (ins "int64_t":$dim, "Type":$dtype, "int64_t":$mod);
  let genVerifyDecl = 1;
  // verifyConstructionInvariants: squarefree(mod) — μ(mod) ≠ 0, mod > 1
}

def CertType : PirtmType<"Cert", "cert"> {
  let parameters = (ins "int64_t":$prime);
  let genVerifyDecl = 1;  // Miller-Rabin; cert is always atomic
}

def CertPairType : PirtmType<"CertPair", "cert_pair"> {
  let parameters = (ins "int64_t":$mod);
  let genVerifyDecl = 1;  // squarefree(mod); factors match input certs
}
```

**Day-0 validation gate** — `mlir-opt --verify-diagnostics` must:

- Accept: `!pirtm.tensor<4,f64,mod=7919>` (prime)
- Reject: `!pirtm.tensor<4,f64,mod=7921>` (= 89×89; not prime, not squarefree)
- Accept: `!pirtm.ctensor<4,f64,mod=59622233>` (7919×7907; squarefree)
- Reject: `!pirtm.ctensor<4,f64,mod=49>` (= 7²; not squarefree)

No downstream work begins until this test passes with correct diagnostics on all four lines.

---

### 2. Session Governance — Three Structural Levels

The contractivity proof and the network-ISS proof are **temporally decoupled** obligations.
Conflating them into a single `epsilon_map` in `pirtm.module` silently omits cross-channel
gain terms and can pass verification on a composite system that is not network-ISS.

| Level | IR Construct | Governance Object | Proof Obligation | Verifier Pass | Phase |
|---|---|---|---|---|---|
| Atomic | `pirtm.module` | Scalar ε, scalar op_norm_T | ‖Ξ‖ + ‖Λ‖·T < 1 − ε | `contractivity-check` | Transpile |
| Tensor | `pirtm.merge` | CRT product mod | gcd(mod₁, mod₂) = 1 | `merge-coprimality` | Transpile |
| Network | `pirtm.session_graph` | Gain matrix Ψ (k×k) | r(Ψ) < 1 | `spectral-small-gain` | **Link** |

**Invariant**: `pirtm.module` carries exactly one `prime_index`, one `epsilon`, one `op_norm_T`.
No multi-prime modules. No `epsilon_map`. Non-negotiable; no future PR may relax it.

**`pirtm.module` TableGen:**

```tablegen
def Pirtm_ModuleOp : Pirtm_Op<"module", [
    IsolatedFromAbove, SymbolTable, SingleBlock
]> {
  let arguments = (ins
    I64Attr:$prime_index,          // must be prime — prime-validity verifier
    F64Attr:$epsilon,              // scalar; governs exactly this module's step ops
    F64Attr:$op_norm_T,            // scalar; matches T used in all child pirtm.step ops
    StrAttr:$identity_commitment
  );
  let regions = (region SizedRegion<1>:$body);
  let verifier = [{ return verifyAtomicModule(*this); }];
}
```

**`pirtm.session_graph` is a link-time construct.** At transpile time, `.pirtm.bc` stubs carry
`gain_matrix = #pirtm.unresolved_coupling` — a sentinel that causes `spectral-small-gain` to
error if invoked before link.

```tablegen
def Pirtm_SessionGraphOp : Pirtm_Op<"session_graph", [
    IsolatedFromAbove, SymbolTable, SingleBlock
]> {
  let arguments = (ins
    F64TensorAttr:$gain_matrix,        // k×k; injected at link time from --coupling
    SymbolRefArrayAttr:$modules,       // references to nested pirtm.module ops
    I64TensorAttr:$session_primes,     // canonical prime_index per session
    StrArrayAttr:$commitments          // debug metadata only
  );
  let verifier = [{ return verifySpectralSmallGain(*this); }];
}

def UnresolvedCouplingAttr : Pirtm_Attr<"UnresolvedCoupling", "unresolved_coupling"> {}
```

---

### 3. Six Verifier Passes — Ordered Pipeline

```
Phase: TRANSPILE
  1. prime-validity          → pirtm.module (prime_index), pirtm.cert
  2. squarefree-validity     → pirtm.ctensor, pirtm.cert_pair
  3. merge-coprimality       → pirtm.merge: gcd(mod₁, mod₂) = 1 at parse time
  4. contractivity-check     → pirtm.step: ε sourced from parent pirtm.module
  5. cert-consumption        → function return: every !pirtm.cert consumed

Phase: LINK
  6. spectral-small-gain     → pirtm.session_graph: r(Ψ) < 1 via power iteration
                               (errors if gain_matrix = #pirtm.unresolved_coupling)
```

Ordering is a pipeline constraint in `mlir-opt`. Out-of-order execution is an error.

---

### 4. Two-Phase Compilation Model

| Phase | LLVM analogue | PIRTM operation | Proof produced |
|---|---|---|---|
| Transpile | Per-TU → `.bc` | `pirtm transpile` per session | Local ISS: ‖Ξ‖ + ‖Λ‖·T < 1 − ε |
| Link | LTO intermodular | `pirtm link` after all modules registered | Network ISS: r(Ψ) < 1 |
| Runtime | Native execution | Rust `pirtm-runtime` kernel | No proof — execution only |

#### `pirtm link` CLI

```
pirtm link [OPTIONS] <module.pirtm.bc>...
  --coupling <coupling.json>   Gain matrix Ψ. Default: conservative identity bound.
  --output   <binary.bin>      Sealed runtime binary.
  --verify-only                spectral-small-gain only; no binary emitted (CI gate).

Exit codes: 0 = all passes; 1 = spectral-small-gain FAIL; 2 = contractivity-check regression.
```

#### coupling.json — Two-Layer Resolution

Ψ_ij is the ISS gain from prime channel j to channel i. `prime_index` is the canonical index;
human names are a link-time alias that does not survive into the IR.

```json
{
  "format": "pirtm-coupling-v1",
  "sessions": {
    "session_a": { "prime_index": 7919, "commitment": "0xabc123" },
    "session_b": { "prime_index": 7907, "commitment": "0xdef456" }
  },
  "gain_matrix": {
    "session_a": { "session_a": 0.0,  "session_b": 0.15 },
    "session_b": { "session_a": 0.20, "session_b": 0.0  }
  }
}
```

Three ordered resolution passes before `spectral-small-gain`:

| Pass | Validates | Error condition |
|---|---|---|
| `name-resolution` | Every name maps to one `prime_index` in a loaded `.pirtm.bc` | Name not found |
| `commitment-crosscheck` | `commitment` matches `.pirtm.bc` `identity_commitment`; no two sessions share one | Mismatch or collision |
| `matrix-construction` | Diagonal = 0.0; off-diagonal ≥ 0.0 | Negative gain or self-coupling |

Emitted IR carries only prime_index-keyed data. Human names are debug metadata.

**Decisive test (Day 14–16)**: Two sessions sharing `commitment: "0xabc123"` must emit
`error: duplicate identity_commitment — sessions must be uniquely identified`.

#### `pirtm inspect` Authoring Tool

```bash
pirtm inspect session_a.pirtm.bc
# prime_index: 7919 | identity_commitment: 0xabc123 | epsilon: 0.05 | op_norm_T: 0.80
```

Workflow: `pirtm transpile` → `pirtm inspect` → author gain values → `pirtm link`.
The only human-authored field in `coupling.json` is the off-diagonal gain values.

#### Registration Window and Re-link

`SessionOrchestrator.register()` maps onto the registration window before `pirtm link`.
Adding a session after seal requires `pirtm relink --add new.pirtm.bc --coupling updated.json`.
r(Ψ') has no monotone relationship to r(Ψ); a stable network can become unstable on addition.

---

### 5. `CompositeTensorType` Lowering — Array-of-Structs

`!pirtm.ctensor<dim, dtype, mod=p₁p₂>` lowers to:

```rust
struct CompositeTensor { t1: AtomicTensor<p1>, t2: AtomicTensor<p2> }
```

`pirtm.project` is a zero-cost field access. CRT isomorphism ℤ/(p₁p₂) ≅ ℤ/p₁ × ℤ/p₂ is
structurally visible in memory. **Rejected**: interleaved buffer, lazy view pair.

---

### 6. `SpectralGovernor` Refactor

**Do not modify `spectral_gov.py` until this ADR is merged.**

```python
SpectralGovernor.local(T_i)                        → (ε_i, op_norm_T_i)   # transpile-time
SpectralGovernor.network(T_list, coupling_matrix)  → Ψ                     # link-time
```

`.network()` exposes the latent zero-off-diagonal assumption in `SessionOrchestrator`.

---

### 7. `mod=` Rename — Timing

Lands atomically on `dialect/pirtm-ir` branch merge at Day 14.
All access sites catalogued in `docs/migration/prime-to-mod-rename.md` before code changes.
Affected: `prime_mapper.py`, `petc_bridge.py`, `orchestrator.py`.
`TranspileSpec.prime_index` keeps its name — only tensor type parameters become `mod=`.

---

### 8. Binary Self-Description — Three-Layer Audit Architecture

Proof metadata and audit chain are **distinct in kind**:

- **Proof metadata** is pre-execution: a property of the code, a universal quantifier over all inputs.
- **Audit chain** is post-execution: a property of one execution trajectory on specific inputs.

Conflating them produces an unsound tool. Treating a clean audit chain as evidence of
contractivity is not logically implied. Embedding a live audit chain in a binary implies the
binary mutates during execution, breaking the sealed-binary model.

| Layer | Location | Written by | Read by | Contains |
|---|---|---|---|---|
| 1. Static proof | `!pirtm_proof` section in `.pirtm.bc` | `pirtm transpile` | `pirtm inspect` (offline) | `prime_index`, `epsilon`, `op_norm_T`, `identity_commitment`, `proof_hash`, pass result |
| 2. Link-time governance | `!pirtm_governance` section in `pirtm_runtime.bin` | `pirtm link` | `pirtm inspect` (offline) | Gain matrix Ψ, r(Ψ), session prime map, `spectral-small-gain` result |
| 3. Runtime audit chain | `AuditChain` in `LambdaTraceBridge` | `pirtm-runtime` execution | `pirtm audit` (requires trace) | Step-level `!pirtm.cert` production/consumption, `QARISession` telemetry |

Layers 1 and 2 are **non-allocating sections** — embedded in the binary file but stripped from
the loaded executable image at runtime (LLVM `SHF_NOALLOC` pattern). Zero runtime overhead.
Zero binary mutation. `pirtm inspect` is a pure file reader.

Layer 3 is strictly runtime. The audit chain records what actually happened; it cannot be
known from the binary alone.

#### Proof Hash — Content-Addressable Certification

The `!pirtm_proof` section carries:

```
proof_hash = H(prime_index ‖ ε ‖ op_norm_T ‖ ‖Ξ‖_op ‖ ‖Λ‖_op)
```

where H is the same commitment function as `identity_commitment` (SHA256 or Poseidon per
configuration). This makes the binary content-addressable: a developer can confirm the exact
(ε, op_norm_T, ‖Ξ‖, ‖Λ‖) triple that was verified without access to the source YAML.

Two binaries with different parameters but the same pass result are distinguishable by hash.

#### `pirtm inspect` — Full Output Specification

```bash
pirtm inspect <file.pirtm.bc | pirtm_runtime.bin> [--layer static|governance|both]

# Example output:
Session Identity
  prime_index:          7919
  identity_commitment:  0xabc123
  proof_hash:           0x7f3a91...  # H(prime‖ε‖T‖‖Ξ‖‖‖Λ‖)

Static Proof  (transpile-time)
  contractivity_check:  PASS
  epsilon:              0.05
  op_norm_T:            0.80
  verified_at:          2026-03-08T17:51:00Z
  pirtm_version:        0.1.0-dialect/pirtm-ir

Link-time Governance  (sealed binary only)
  session_count:        2
  session_primes:       [7919, 7907]
  spectral_radius:      0.412
  spectral_small_gain:  PASS
  sealed_at:            2026-03-08T17:55:00Z

Audit Chain: NOT EMBEDDED — retrieve via `pirtm audit <trace.log>`
```

The final line is a **required design signal**, not optional output. It prevents the failure
mode where an operator treats a clean `pirtm inspect` as evidence the system ran safely,
rather than that it was *designed* safely. The distinction is the soundness boundary.

#### `pirtm audit` — Runtime Complement

```bash
pirtm audit <trace.log> --binary <pirtm_runtime.bin>

# Cross-references runtime cert production against static proof_hash
# Confirms execution ran on the verified binary (chain-of-custody check)
# Reports: certs produced, certs consumed, unconsumed certs (runtime cert-consumption violations)
```

The `--binary` flag enables cross-referencing the runtime trace against the static proof hash,
confirming the execution was on the same binary that was verified. Full chain of custody:
transpile-time proof → link-time governance seal → runtime cert accumulation → offline audit.

#### Implementation — ~30 lines, zero new TableGen

In MLIR: add a `pirtm.proof` op at module body top level — a metadata op with no execution
semantics, carrying four fields: `prime_index`, `epsilon`, `op_norm_T`, `proof_hash`.
Maps to LLVM module-level metadata (`!llvm.module.flags` / `Module::addModuleFlag` pattern).
SECTION: `SHF_NOALLOC`; excluded from runtime executable image.

---

## Predicted Failure Modes (write tests before implementation)

1. **First `pirtm link` fails r(Ψ) = 1.0** (conservative identity bound). Fix is in session
   design. A negative test for this must ship with `pirtm link`.

2. **Commitment collision** (Day 14–16 gate): Two sessions sharing `"0xabc123"` must emit
   `error: duplicate identity_commitment`. Decisive test for the two-layer model.

3. **`pirtm.project` is a parse-time total function**: `mod % prime == 0` is O(1) after
   `squarefree-validity`. No runtime projection failures possible.

4. **`pirtm inspect` round-trip** (Day 14 gate extension):
   ```bash
   pirtm transpile examples/basic.yaml --output basic.pirtm.bc
   pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"
   ```
   If this passes, a developer who has never seen the source YAML can confirm the contractivity
   invariant from the compiled artifact alone. That property — the proof travels with the code
   — is the foundational guarantee this section enables.

5. **`SpectralGovernor.network()` reveals ε is over-tight** under conservative bound.
   Correct lifecycle: start conservative → profile → tighten coupling → loosen ε.

---

## Sequenced Artifact Plan

| Day | Artifact | Gate condition |
|---|---|---|
| 0 | This ADR merged | No downstream work before merge |
| 0 | `docs/migration/prime-to-mod-rename.md` | Every `.prime` access site catalogued |
| 0–3 | `src/pirtm/dialect/pirtm.td` — 4 TypeDefs + `session_graph` stub | Four-line `--verify-diagnostics` passes |
| 3–7 | `pirtm.merge` op + `merge-coprimality` verifier; `pirtm.proof` metadata op in `mlir_emitter.py` | Coprime merge passes; non-coprime emits diagnostic |
| 7–14 | `src/pirtm/transpiler/mlir_emitter.py` full round-trip | All `examples/` round-trip via `--output mlir` |
| 14 | Merge `dialect/pirtm-ir` → `main`; `pirtm inspect` static-proof read | `mod=` rename lands atomically; `pirtm inspect basic.pirtm.bc | grep PASS` |
| 14–16 | `src/pirtm/transpiler/pirtm_link.py` — 3 resolution passes | Commitment-collision test passes |
| 30 | `pirtm link` CLI + `spectral-small-gain` pass + `!pirtm_governance` section | r=0.7 passes; r=1.1 fails; `pirtm inspect` reads governance layer |
| 30 | `pirtm audit` CLI (runtime trace cross-reference) | Chain-of-custody test: modified binary detected |
| 90 | `src/pirtm_core/` Rust crate + PyO3 bindings | `pirtm.step` ≥10× NumPy on 512-dim tensor |
