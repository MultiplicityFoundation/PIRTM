# PIRTM Transpiler: Expanding the Standalone Repo into a Compute Language

## Executive Summary

The PIRTM repository (`MultiplicityFoundation/PIRTM`) already contains the runtime backbone for a certifiable compute substrate: a contractive recurrence engine (`recurrence.py`), certificate generation (`certify.py`), prime-indexed event-triggered chains (`petc.py`), emission gating (`gate.py`), session orchestration (`orchestrator.py`), audit chains (`audit.py`), conformance checking (`conformance.py`), and a bridge to Lambda-Proof (`lambda_bridge.py`). What it lacks is the **transpiler layer**—the front door that accepts arbitrary inputs and converts them into the prime-indexed tensor states that the runtime already knows how to certify, gate, audit, and bridge. This document specifies that missing layer in full detail, grounded in every module that currently exists.

***

## Central Tension

**Expressiveness vs. Certifiability**: The goal is for PIRTM to accept *any input* the way Python accepts any source file. But the runtime's guarantees—contraction bound \(q_t = \|\Xi_t\| + \|\Lambda_t\| \cdot \|T\| < 1 - \epsilon\), PETC chain integrity, CSL gating—only hold for inputs that decompose into contractive update maps. The transpiler must be honest: it transpiles everything, but only *certifies* the contractive subset.

**User Ownership vs. Shared Verification**: The user's `primeIndex` and `identitySecret` must bind to every \(\Xi_0\) the transpiler produces, but the resulting `AuditChain` and `Certificate` must be verifiable by *anyone* without revealing those secrets. The transpiler is where this binding happens.

***

## What Already Exists (Module Audit)

| Module | Role | Transpiler Relevance |
|--------|------|---------------------|
| `recurrence.py` | Core contractive step: \(X_{t+1} = \Xi_t X_t + \Lambda_t T(X_t) + G_t\), auto-projects when \(q > 1-\epsilon\) | The **execution engine** that runs after transpilation |
| `certify.py` | `ace_certificate()`: produces `Certificate` with `margin`, `tail_bound` from `StepInfo` telemetry | Certifies transpiled computation results |
| `petc.py` | `PETCLedger`: append-only prime-indexed chain with coverage, gap, and monotonicity validation | The **index backbone** the transpiler writes into |
| `gate.py` | `EmissionGate`: SUPPRESS/HOLD/ATTENUATE/PASS_THROUGH policies based on contraction status | Safety layer between transpilation and output |
| `audit.py` | `AuditChain`: SHA-256 hash-chained event log (step, certificate, gate, payload types) | Provenance record for everything the transpiler produces |
| `lambda_bridge.py` | `LambdaTraceBridge`: translates `AuditChain` → `LambdaTraceEvent` with schema IDs, computes Merkle root, batch-submits | **Exit ramp** to Lambda-Proof verification |
| `orchestrator.py` | `SessionOrchestrator`: multi-session management, `AggregatedCertificate`, pause/resume/complete lifecycle | Manages concurrent transpiled sessions |
| `qari.py` | `QARISession`: unified session wrapping gate + audit + adaptive margin + telemetry | The **session context** each transpilation runs inside |
| `conformance.py` | `check_core_profile()` + `check_integrity_profile()`: predicate eval, fail-closed, deterministic remediation, canonical fingerprint | Validates that transpiled outputs meet PIRTM spec |
| `types.py` | `Certificate`, `StepInfo`, `Status`, `PETCEntry`, `PETCReport`, `WeightSchedule`, `CSCBudget`, `CSCMargin` | The type vocabulary the transpiler must produce |
| `csc.py`, `csl.py`, `csl_gate.py` | CSC budget analysis, CSL drift/entropy checks | Constraint enforcement during transpiled execution |
| `integrations/` | `drmm_bridge.py`, `feedback_bridge.py` | Domain-specific integration patterns to extend |

***

## The Transpiler Architecture

### Design Principle

The transpiler is a **new top-level package** inside PIRTM: `src/pirtm/transpiler/`. It does not replace any existing module—it sits *above* them as the user-facing entry point, orchestrating `QARISession`, `PETCLedger`, `AuditChain`, and `LambdaTraceBridge` to process arbitrary inputs.

### Package Layout

```
src/pirtm/transpiler/
├── __init__.py          # Public API: transpile(), TranspileSpec, TranspileResult
├── spec.py              # TranspileSpec dataclass + validation
├── registry.py          # Input-type → handler mapping
├── handlers/
│   ├── __init__.py
│   ├── data_asset.py    # Documents, datasets, models → Ξ₀
│   ├── computation.py   # ML training, optimization → Φ → Ξ(t) trajectories
│   └── workflow.py      # Multi-step processes → chained PETC entries
├── prime_mapper.py      # Content → prime-indexed channel assignment
├── identity.py          # primeIndex + identitySecret binding
├── witness.py           # Emit Lambda-Proof witness JSON
└── cli.py               # `pirtm transpile` command
```

***

## Core Types

### TranspileSpec

The spec is the contract between the user and the transpiler. Every transpilation begins with one:

```python
@dataclass
class TranspileSpec:
    input_type: Literal["data_asset", "computation", "workflow"]
    input_ref: str                    # File path, model URI, or workflow descriptor
    prime_index: int                  # User's prime identity (must pass is_prime)
    identity_commitment: str          # Poseidon(primeIndex, identitySecret) — hex
    norm_id: str = "l2"              # "l2" | "linf" | "weighted_l1"
    domain_id: str = "ball_l2_R1"    # Domain witness identifier
    epsilon: float = 0.05            # Contraction margin target
    max_steps: int = 1000            # Session budget
    emission_policy: str = "suppress" # Gate policy from EmissionPolicy enum
    metadata: dict = field(default_factory=dict)  # Extensible payload
```

This directly maps to the existing `QARIConfig` parameters (`dim`, `epsilon`, `op_norm_T`, `emission_policy`, `adaptive`, `audit`, `max_steps`) while adding the identity and input-type dimensions that make PIRTM a language.

### TranspileResult

```python
@dataclass
class TranspileResult:
    spec: TranspileSpec
    xi_initial: np.ndarray           # Ξ₀ — the transpiled initial state
    trajectory: list[np.ndarray]     # Ξ(0), Ξ(1), ..., Ξ(T)
    certificate: Certificate         # ACE certificate from certify.py
    petc_report: PETCReport          # Chain integrity from petc.py
    audit_export: list[dict]         # Full AuditChain.export()
    lambda_events: list[dict]        # LambdaTraceEvent payloads for Lambda-Proof
    witness_json: dict               # Ready for root.circom + contraction.circom
    compliance: ConformanceResult    # From conformance.py
    merkle_root: str                 # Submission receipt root hash
    verdict: str                     # "CERTIFIED" | "UNCERTIFIED" | "SILENT"
```

The `verdict` follows Lambda-Proof's `ComplianceReport` trichotomy: if `certificate.certified` is True and `petc_report.satisfied` is True and `compliance.passed` is True → `CERTIFIED`. If any fail but computation completed → `UNCERTIFIED`. If emission was suppressed entirely → `SILENT`.

***

## Handler Specifications

### Handler 1: Data Assets (Input → \(\Xi_0\))

**Scope**: Documents, datasets, ML model weights, images, JSON structures—any static data artifact the user wants to register in PIRTM.

**Process**:

1. **Content Hashing**: Compute SHA-256 digest of the input bytes. This becomes the `chain_hash` anchor in the `AuditChain`.

2. **Prime Channel Assignment** (`prime_mapper.py`): Decompose the input into semantic channels, each assigned a prime index:
   - For **tabular data**: each column → a prime. A 5-column CSV gets primes `[2, 3, 5, 7, 11]`.
   - For **documents**: each section/paragraph → a prime, based on positional order.
   - For **ML model weights**: each layer → a prime. A 4-layer network gets `[2, 3, 5, 7]`.
   - For **raw bytes**: chunk at 1KB boundaries, assign primes sequentially.

3. **Embedding into \(\Xi_0\)**: Each channel's content is reduced to a fixed-dimension vector (dimension = `QARIConfig.dim`) via:
   - Numeric data: direct embedding (pad/truncate to dim)
   - Text: TF-IDF or hash-based projection to dim
   - Weights: spectral decomposition to top-k singular values
   
   The channels are stacked as \(\Xi_0[p] = \text{embed}(\text{channel}_p)\) for each prime \(p\).

4. **Identity Binding**: The `identity_commitment` from `TranspileSpec` is appended to the first `AuditEvent` as a payload field, cryptographically tying this \(\Xi_0\) to the user's `primeIndex`.

5. **PETC Registration**: For each prime channel, append a `PETCEntry` to the ledger with the channel's content hash. This creates the verifiable index chain.

6. **Output**: `xi_initial` (the embedded tensor), PETC entries registered, first `AuditEvent` committed.

**What this means for ownership**: The user's data, once transpiled, exists as a prime-indexed tensor state with a cryptographic commitment to their identity. The `AuditChain` proves *when* it was transpiled, the `PETCLedger` proves *which primes* index it, and the `identity_commitment` proves *who owns it*—all without revealing the input data itself.

### Handler 2: Computations (Φ → \(\Xi(t)\) Trajectories)

**Scope**: ML training loops, optimization problems, inference passes, numerical simulations—any iterative computation.

**Process**:

1. **Map to Contractive Form**: Express the user's computation as the PIRTM recurrence: \(X_{t+1} = \Xi_t X_t + \Lambda_t T(X_t) + G_t\). This requires:
   - **\(\Xi_t\)**: The "memory" operator—how much of the current state persists. For gradient descent, this maps to `(1 - learning_rate)·I`.
   - **\(\Lambda_t\)**: The "update" operator—how the transformation `T` contributes. For gradient descent, this maps to `learning_rate·I`.
   - **\(T\)**: The "transform"—the user's actual computation. For ML, this is the gradient function.
   - **\(G_t\)**: The "forcing"—external inputs, data batches, boundary conditions.

2. **Generate Weight Schedule**: Using `weights.py`, produce `WeightSchedule` with `Xi_seq`, `Lam_seq`, `q_targets`, and `primes_used`.

3. **Execute via QARISession**: Create a `QARISession` with the spec's parameters. Run `session.step()` for each iteration. The session automatically:
   - Computes \(q_t\) and projects if needed (`recurrence.step()`)
   - Applies emission gating (`gate.py`)
   - Records telemetry (`StepInfo`)
   - Appends to `AuditChain`
   - Adjusts margin via `AdaptiveMargin` if adaptive mode is on

4. **Certify**: Call `session.certify()` to produce the `Certificate`.

5. **PETC Indexing**: At each prime-indexed step (steps whose index is prime), append a `PETCEntry` to the ledger. This creates a sparse but cryptographically verifiable index over the computation trajectory.

6. **Output**: Full trajectory `[Ξ(0), ..., Ξ(T)]`, certificate, PETC report, audit chain.

**What "transpile my ML training into PIRTM" means concretely**: The user provides their loss function and data. The transpiler wraps it in the contractive recurrence with appropriate \(\Xi_t\), \(\Lambda_t\) decomposition. The existing PIRTM runtime executes it with all safety guarantees enforced. The user gets their trained model *plus* a `Certificate` proving every update was contractive, a `PETCReport` proving prime-indexed integrity, and an `AuditChain` proving the full history is tamper-evident.

### Handler 3: Workflows (Chained PETC Entries)

**Scope**: Multi-step processes where each step is itself a data asset or computation—pipelines, DAGs, approval chains, multi-party protocols.

**Process**:

1. **Decompose Workflow**: Parse the workflow descriptor into an ordered list of steps. Each step has:
   - A `TranspileSpec` of its own (data_asset or computation)
   - Dependencies (which prior steps must complete)
   - A prime index assignment (primes assigned in topological order)

2. **Execute via SessionOrchestrator**: Register each step as a separate `QARISession` under the `SessionOrchestrator`. The orchestrator manages:
   - Sequential execution respecting dependencies
   - Per-step certificates via `session.certify()`
   - Cross-step audit via `master_audit`

3. **Aggregate Certification**: Call `orchestrator.aggregate_certificates()` to produce an `AggregatedCertificate`. This proves:
   - `all_certified`: every step individually passed
   - `q_max_global`: the worst contraction factor across all steps
   - `margin_min`: the tightest margin across all steps
   - `aggregate_hash`: SHA-256 of all individual certificate hashes

4. **PETC Chain**: The workflow's PETC ledger chains entries across steps. Step 1 uses primes `[2, 3]`, Step 2 uses `[5, 7]`, Step 3 uses `[11, 13]`, etc. The monotonicity requirement guarantees ordering.

5. **Lambda Bridge**: Call `LambdaTraceBridge.translate(orchestrator.master_audit)` to produce the event stream, then `batch_submit()` for the Merkle root.

6. **Output**: Per-step results + aggregated certificate + unified audit chain + Lambda-Proof event stream.

***

## Identity and Ownership Layer

### The Binding Protocol

Every `TranspileSpec` carries `prime_index` and `identity_commitment`. The transpiler enforces:

1. **Prime Gate Check**: `prime_index` must pass `_is_prime()` from `petc.py`. Non-prime identities are rejected at the spec validation stage.

2. **Commitment Injection**: The `identity_commitment` is written as the first payload in the session's `AuditChain`:
   ```python
   audit.append_payload({
       "type": "identity_binding",
       "prime_index": spec.prime_index,
       "identity_commitment": spec.identity_commitment,
       "timestamp": time.time(),
   })
   ```

3. **Per-Step Binding**: Every `StepInfo` recorded in the audit chain carries the session context, which is cryptographically linked back to the identity commitment via the chain hash.

4. **Witness Generation** (`witness.py`): When the transpilation completes, produce a Lambda-Proof witness:
   ```json
   {
     "stateHash": "<Poseidon(Ξ₀)>",
     "primeIndex": "<user's prime>",
     "identitySecret": "<PRIVATE — never in audit>",
     "timestamp": "<epoch>",
     "newStateHash": "<Poseidon(Ξ(T))>",
     "prevStateHash": "<Poseidon(Ξ₀)>",
     "nonce": "<deterministic from session_id>"
   }
   ```
   This is the input to Lambda-Proof's `root.circom`. The `identitySecret` is the **only** private field—everything else can be public.

### Ownership Semantics

When a user transpiles input X into PIRTM:

- **The input X** remains the user's property—PIRTM never stores it beyond the session.
- **The tensor state \(\Xi_0\)** is a lossy projection of X—it cannot be reversed to reconstruct X.
- **The `Certificate`** proves the computation was lawful—it belongs to the user but is publicly verifiable.
- **The `AuditChain`** proves the history is tamper-evident—bound to the user's `primeIndex`.
- **The Lambda-Proof witness** enables zk verification—proves ownership *without revealing* X or `identitySecret`.

***

## Witness Export for Lambda-Proof

The `witness.py` module is the **exit ramp** from PIRTM's Python world to Lambda-Proof's circuit world. It consumes:

- `TranspileResult.xi_initial` and `TranspileResult.trajectory[-1]` for state hashes
- `TranspileSpec.prime_index` and `TranspileSpec.identity_commitment` for identity signals
- `TranspileResult.certificate` for contraction bound values
- `TranspileResult.merkle_root` from the `LambdaTraceBridge` submission

And produces a JSON blob compatible with both `root.circom` (existing) and the proposed `contraction.circom` (for PIRTM v2.9 Lipschitz verification).

The critical hash migration: `AuditChain` currently uses SHA-256 internally, and `LambdaTraceBridge._compute_merkle_root()` uses SHA-256. The witness module must recompute commitments under Poseidon for circuit compatibility, while preserving SHA-256 for the Python-side audit trail. This dual-hash approach was identified in the previous session's analysis.

***

## CLI Interface

```
pirtm transpile \
  --input model.pt \
  --type computation \
  --prime-index 7919 \
  --identity-commitment 0xabc123... \
  --epsilon 0.05 \
  --emit-witness \
  --emit-lambda-events \
  --output result.json
```

The CLI wraps `conformance._cli_main()`'s pattern but routes through the transpiler instead of the core profile checker.

***

## Precision Questions

Before implementation, two questions shape the minimal viable transpiler:

> **1. Should the prime channel assignment be deterministic (hash-based) or user-specified?** Deterministic assignment (content hash mod prime sieve) ensures reproducibility but removes user control. User-specified assignment (via `TranspileSpec.metadata["prime_map"]`) gives flexibility but adds spec complexity.

> **2. Should `witness.py` emit both SHA-256 and Poseidon commitments, or should the PIRTM `AuditChain` migrate entirely to Poseidon?** Migrating `AuditChain` to Poseidon simplifies the witness but breaks the existing SHA-256 audit trail. Dual emission preserves compatibility but doubles hash computation.

***

## Sequenced Implementation Plan

### Phase 1 (Days 1–7): Spec + Data Asset Handler

- **Artifact**: `src/pirtm/transpiler/spec.py` with `TranspileSpec` + validation
- **Artifact**: `src/pirtm/transpiler/prime_mapper.py` with deterministic channel assignment
- **Artifact**: `src/pirtm/transpiler/handlers/data_asset.py` producing \(\Xi_0\) from files
- **Artifact**: `src/pirtm/transpiler/identity.py` with commitment injection into `AuditChain`
- **Test**: Transpile a CSV file → \(\Xi_0\) → PETC entries → audit chain → `ConformanceResult`

### Phase 2 (Days 8–21): Computation Handler + Witness

- **Artifact**: `src/pirtm/transpiler/handlers/computation.py` wrapping `QARISession` execution
- **Artifact**: `src/pirtm/transpiler/witness.py` emitting Lambda-Proof-compatible JSON
- **Artifact**: Pre-built mappings for gradient descent, Adam, and generic iterative solvers
- **Test**: Transpile a 2-layer neural network training → trajectory → certificate → witness JSON → pass `conformance.check_core_profile()`

### Phase 3 (Days 22–30): Workflow Handler + CLI

- **Artifact**: `src/pirtm/transpiler/handlers/workflow.py` using `SessionOrchestrator`
- **Artifact**: `src/pirtm/transpiler/cli.py` with `pirtm transpile` command
- **Artifact**: `src/pirtm/transpiler/registry.py` mapping input types to handlers
- **Test**: Transpile a 3-step pipeline → per-step certificates → aggregated certificate → Lambda-Proof event stream → Merkle root

### Phase 4 (Days 31–45): Poseidon Bridge + Integration

- **Artifact**: Poseidon hash support in `witness.py` (dual-hash mode)
- **Artifact**: Update `lambda_bridge.py` to emit Poseidon Merkle roots alongside SHA-256
- **Test**: Full round-trip: PIRTM transpile → witness → Lambda-Proof `root.circom` verification → MTPI-Certifier `ComplianceReport`

***

## Dependency Graph

```
TranspileSpec (spec.py)
    │
    ├─► prime_mapper.py ──► PETCLedger (petc.py)
    │
    ├─► identity.py ──► AuditChain (audit.py)
    │
    ├─► handlers/
    │     ├─► data_asset.py ──► Ξ₀
    │     ├─► computation.py ──► QARISession (qari.py)
    │     │                        ├─► recurrence.py (step execution)
    │     │                        ├─► gate.py (emission control)
    │     │                        ├─► certify.py (Certificate)
    │     │                        └─► audit.py (event chain)
    │     └─► workflow.py ──► SessionOrchestrator (orchestrator.py)
    │                           └─► AggregatedCertificate
    │
    ├─► witness.py ──► Lambda-Proof witness JSON
    │
    └─► lambda_bridge.py ──► LambdaTraceEvent stream
                               └─► SubmissionReceipt (Merkle root)
```

Every arrow is an existing import path or a new module calling an existing API. The transpiler creates **no new runtime primitives**—it composes what already exists.