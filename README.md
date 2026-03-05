# PIRTM — Prime-Indexed Recursive Tensor Mathematics

**PIRTM** is a computation language and certified runtime for recursive tensor mathematics. It is a foundational component of [Multiplicity Theory](https://github.com/MultiplicityFoundation) and the [ΛProof](https://github.com/MultiplicityFoundation) open foundation — a framework for building verifiable, ethically governed, and provably stable dynamic systems.

Every well-formed PIRTM program carries four guarantees that distinguish it from conventional numerical libraries:

1. **Contractive typing** — every expression includes a proof that the recurrence contracts by at least $\epsilon > 0$; unbounded divergence is impossible by construction.
2. **Prime-indexed ordering** — every computation step is assigned a prime number as its audit-chain position, giving a total, gap-bounded, tamper-evident ordering over all events.
3. **Emission predication** — output is not produced by execution alone; it is produced only when a language-level gate predicate (including ethical CSL checks) is satisfied.
4. **Witness commitment** — every emitted output binds *(state hash × prime index × contraction certificate)* into a single commitment that can be verified without re-executing the computation.

These properties make PIRTM suitable as the safety-critical inner loop for AI inference engines, certified control systems, and any computation that must be auditable after the fact.

## Purpose and Design Principles

Classical numerical frameworks give you correctness by convention — the caller is responsible for stability and safety. PIRTM inverts this: **safety is enforced by the type system and runtime, not by caller discipline**.

- **Certified stability**: every step projects gain matrices so the contraction coefficient `q_t < 1 − ε` holds invariantly. No configuration can produce unbounded growth.
- **Auditable execution**: the `AuditChain` attaches a prime index and cryptographic hash to every step, producing a Merkle-verifiable trace that travels with the computation.
- **Ethical emission gating**: the Conscious Sovereignty Layer (CSL) operators — Neutrality, Beneficence, Silence, and Commutation — evaluate each step against ethical predicates before output is released. Failing steps default to NO-OP with a logged audit event.
- **Composable governance**: `SpectralGovernor` derives safety parameters from the operator `T` itself; `SessionOrchestrator` federates multiple sessions; `LambdaTraceBridge` submits audit chains to the ΛProof on-chain system.

## Open Foundation

PIRTM's mathematical core — including the contractive recurrence, PETC prime ordering, CSL operators, and contraction safety certificates — is part of the **Constitutional Core** irrevocably dedicated to the public domain by the [ΛProof Open Mathematical Foundation Pledge](PATENT%20PLEDGE.md). Anyone may implement, extend, or build commercial products on these foundations without license or royalty obligation.

## Current Release: `v0.1.0` (2026-03-01)

| Subsystem | Status | Stability |
|---|---|---|
| Core recurrence / certification (`recurrence`, `certify`, `projection`) | Active | **Stable** |
| Planning / validation (`petc`, `weights`, `gain`, `csc`) | Active | **Stable** |
| Runtime governance (`gate`, `telemetry`, `audit`, `qari`) | Active | **Stable** |
| Protocol integration (`csl`, `csl_gate`, `spectral_gov`, `orchestrator`, `lambda_bridge`, `petc_bridge`) | Active | **Stable** |
| ACE package (`pirtm.ace.*`) | Active | Experimental → stabilizing |
| Transpiler (`pirtm.transpiler.*`) | Active | Stabilizing |
| Legacy surfaces (`pirtm._legacy`) | Active | **Deprecated** — sunset in `v0.3.0` |

Repository directories `frontend/`, `notebooks/`, and `papers/` are outside the `v0.1.0` package scope and are not covered by the public API contract.

## What It Does

PIRTM provides a contractive recurrence loop

\[
X_{t+1} = P\left(\Xi_t X_t + \Lambda_t T(X_t) + G_t\right)
\]

with safety projection (`q_t < 1 - epsilon`), ACE certificates, ISS bounds, PETC chain validation, weight/gain synthesis, and CSC budget tooling.

## Install

- Core install: `pip install -e .`
- Dev tools: `pip install -e ".[dev]"`
- Full legacy + dev extras: `pip install -e ".[all]"`

## Quickstart

```python
import numpy as np
from pirtm import step, ace_certificate

x = np.ones(4)
xi = 0.3 * np.eye(4)
lam = 0.2 * np.eye(4)
T = lambda v: 0.8 * v
G = np.zeros(4)
P = lambda v: v

x_next, info = step(x, xi, lam, T, G, P, epsilon=0.05, op_norm_T=0.8)
cert = ace_certificate(info)
print(info.q, cert.certified)
```

## Modules

- `pirtm.recurrence`: `step`, `run`
- `pirtm.projection`: soft / weighted-`\ell_1` projection
- `pirtm.certify`: `ace_certificate`, `iss_bound`
- `pirtm.petc`: `PETCLedger`, `petc_invariants`
- `pirtm.weights`: `synthesize_weights`, `validate_schedule`
- `pirtm.gain`: `estimate_operator_norm`, `build_gain_sequence`, `check_iss_compatibility`
- `pirtm.csc`: `solve_budget`, `compute_margin`, `multi_step_margin`, `sensitivity`
- `pirtm.gate`: `EmissionGate`, `EmissionPolicy`, `gated_run`
- `pirtm.telemetry`: `TelemetryBus`, sinks (`NullSink`, `MemorySink`, `FileSink`, `CallbackSink`)
- `pirtm.audit`: `AuditChain` for deterministic hash-chained trace export
- `pirtm.qari`: `QARISession`, `QARIConfig` high-level adapter
- `pirtm.csl` + `pirtm.csl_gate`: CSL operators and two-stage ethical emission gating
- `pirtm.spectral_decomp` + `pirtm.spectral_gov`: spectral analysis and governance recommendations (supported public spectral APIs for `v0.1.x`; legacy spectral paths in `pirtm._legacy` are deprecated)
- `pirtm.orchestrator`: multi-session registration, pause snapshots, certificate aggregation
- `pirtm.lambda_bridge`: Λ-trace translation + batch submission receipts
- `pirtm.petc_bridge`: prime-indexed ordering allocator for session audit chains
- `pirtm.adaptive`, `pirtm.fixed_point`, `pirtm.monitor`, `pirtm.infinite_prime`

## Tier 7 Quick Example

```python
import numpy as np
from pirtm import (
    EmissionGate,
    EmissionPolicy,
    CSLEmissionGate,
    SpectralGovernor,
    QARIConfig,
    SessionOrchestrator,
)

T = lambda x: 0.8 * x
gov = SpectralGovernor(dim=4)
epsilon, op_norm, _ = gov.govern(T)

contract_gate = EmissionGate(policy=EmissionPolicy.PASS_THROUGH)
csl_gate = CSLEmissionGate(contract_gate)

orchestrator = SessionOrchestrator()
config = QARIConfig(dim=4, epsilon=epsilon, op_norm_T=op_norm, emission_policy=EmissionPolicy.SUPPRESS)
session = orchestrator.register("session-1", config)

X = np.ones(4)
Xi = 0.2 * np.eye(4)
Lam = 0.2 * np.eye(4)
G = np.zeros(4)

out = csl_gate(X, Xi, Lam, T, G, lambda x: x, step_index=0, epsilon=epsilon, op_norm_T=op_norm)
if out.emitted:
    session.step(X, Xi, Lam, T, G)
```

## Tier 7 Runnable Snippets

Single-script smoke example covering each Tier 7 module:

```python
import numpy as np
from pirtm import (
	StepInfo,
	evaluate_csl,
	EmissionGate,
	EmissionPolicy,
	CSLEmissionGate,
	SpectralGovernor,
	QARIConfig,
	SessionOrchestrator,
	AuditChain,
	LambdaTraceBridge,
	PETCAllocator,
)


def mk_info(step: int = 0, residual: float = 0.01) -> StepInfo:
	return StepInfo(
		step=step,
		q=0.4,
		epsilon=0.05,
		nXi=0.2,
		nLam=0.2,
		projected=False,
		residual=residual,
	)


# Shared state
T = lambda x: 0.8 * x
P = lambda x: x
X = np.ones(2)
Xi = 0.2 * np.eye(2)
Lam = 0.2 * np.eye(2)
G = np.zeros(2)

# 1) pirtm.csl
verdict = evaluate_csl(T, X, T(X), mk_info(), step_index=0)
print("csl:", verdict.violations)

# 2) pirtm.csl_gate
gate = CSLEmissionGate(EmissionGate(policy=EmissionPolicy.PASS_THROUGH))
gate_out = gate(X, Xi, Lam, T, G, P, step_index=0, epsilon=0.05, op_norm_T=0.8)
print("csl_gate:", gate_out.emitted, gate_out.final_policy)

# 3) pirtm.spectral_gov
gov = SpectralGovernor(dim=2)
epsilon, op_norm, report = gov.govern(T)
print("spectral_gov:", epsilon, op_norm, report.contraction_feasible)

# 4) pirtm.orchestrator
orch = SessionOrchestrator()
cfg = QARIConfig(dim=2, epsilon=epsilon, op_norm_T=op_norm, emission_policy=EmissionPolicy.PASS_THROUGH)
session = orch.register("s1", cfg)
session.step(X, Xi, Lam, T, G)
agg = orch.aggregate_certificates(["s1"])
print("orchestrator:", agg.all_certified)

# 5) pirtm.lambda_bridge
chain = AuditChain()
chain.append_step(mk_info(step=0))
bridge = LambdaTraceBridge(session_id="demo")
bridge.translate(chain)
receipt = bridge.batch_submit()
print("lambda_bridge:", receipt.status, receipt.events_submitted)

# 6) pirtm.petc_bridge
for i in range(1, 3):
	chain.append_step(mk_info(step=i))
allocator = PETCAllocator(max_sessions=10)
tagged = allocator.tag_audit_chain("session-a", chain)
ordering = allocator.verify_global_ordering()["globally_ordered"]
print("petc_bridge:", tagged[0], ordering)
```

## Documentation

- Docs index: `docs/README.md`
- Requirements matrix: `docs/requirements.md`
- Active roadmap: `docs/plans/PIRTM Core Completion.md`
- Plans status + support matrix: `docs/plans/README.md`
- API reference: `docs/api/README.md`
- Architecture guide: `docs/architecture.md`
- PIRTM Language Specification (Normative): `docs/PIRTM_LANGUAGE_SPEC.md`
- PIRTM Mathematical Specification (Implementation Reference): `docs/math_spec.md`
- Examples index: `examples/README.md` (includes transpiler descriptor usage and `--emit-witness` / `--emit-lambda-events` JSON output gating notes)
- Test guide: `tests/README.md`
- Release notes: `CHANGELOG.md` (`v0.1.0` section)
- Migration notes: `docs/migration/v0.1.0.md` and `docs/migration/certify-v1.md`

## Release Scope (`v0.1.0`)

- The `v0.1.0` package scope and stability contract apply to the Python library under `src/pirtm` and documented CLI surfaces.
- Repository directories `frontend/`, `notebooks/`, and `papers/` are out of package release scope for `v0.1.0` and are not covered by the `pirtm` public API contract.
- Legacy internals under `pirtm._legacy` remain transitional/deprecated and are excluded from stable API guarantees. Sunset target: `v0.3.0`.
- The stability matrix above (under "Current Release") is the canonical support contract for `v0.1.0`.

## Development

```bash
git clone https://github.com/MultiplicityFoundation/PIRTM.git
cd PIRTM
pip install -e ".[dev]"
python -m pytest -q
```

## Conformance and Release Targets

- Run conformance checks:

```bash
pirtm-conformance --profile all --output text
```

## Transpiler CLI (Phase 2.1)

Computation transpilation is available from the command line.

Use the checked-in descriptor file: `examples/transpile_computation.json`.

```bash
pirtm transpile \
	--type computation \
	--input examples/transpile_computation.json \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 3 \
	--emission-policy pass_through \
	--output summary
```

Same path via module entrypoint:

```bash
python -m pirtm transpile \
	--type computation \
	--input examples/transpile_computation.json \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 3 \
	--emission-policy pass_through \
	--output summary
```

Structured JSON result with inline computation descriptor:

```bash
python -m pirtm.cli transpile \
	--type computation \
	--input examples/transpile_computation.json \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 3 \
	--emission-policy pass_through \
	--output json
```

Default JSON output omits `witness_json` and `lambda_events`. Include them explicitly when needed:

```bash
python -m pirtm transpile \
	--type computation \
	--input examples/transpile_computation.json \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 3 \
	--output json \
	--emit-witness \
	--emit-lambda-events
```

Hash controls for witness export:

```bash
python -m pirtm transpile \
	--type computation \
	--input examples/transpile_computation.json \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 3 \
	--hash-scheme poseidon_compat \
	--output json
```

```bash
python -m pirtm transpile \
	--type computation \
	--input examples/transpile_computation.json \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 3 \
	--hash-scheme sha256 \
	--dual-hash \
	--output json
```

Dual-hash witness fields now include `stateHashSha256`, `stateHashPoseidon`, `merkleRootSha256`, `merkleRootPoseidon`, with `hashSchemes` indicating active exports.

Witness schema by hash mode:

| Hash mode | Exact output keys |
| --- | --- |
| `sha256` | `stateHash`, `prevStateHash`, `newStateHash`, `merkleRoot` |
| `poseidon_compat` | `stateHash`, `prevStateHash`, `newStateHash`, `merkleRoot` |
| `dual` (or `--dual-hash`) | `stateHash`, `prevStateHash`, `newStateHash`, `merkleRoot`, `stateHashSha256`, `prevStateHashSha256`, `newStateHashSha256`, `stateHashPoseidon`, `prevStateHashPoseidon`, `newStateHashPoseidon`, `merkleRootSha256`, `merkleRootPoseidon`, `hashSchemes` |

Phase 2.2 mode examples (inline descriptor metadata):

```bash
python -m pirtm transpile \
	--type computation \
	--input examples/transpile_computation.json \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 3 \
	--emission-policy pass_through \
	--metadata '{"mode":"adam","steps":6,"learning_rate":0.1,"beta1":0.9,"beta2":0.99,"initial_state":[1,1,1],"target_state":[0,0,0]}' \
	--output summary
```

```bash
python -m pirtm transpile \
	--type computation \
	--input examples/transpile_computation.json \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 2 \
	--emission-policy pass_through \
	--metadata '{"mode":"iterative_solver","steps":5,"relaxation":0.25,"initial_state":[1,1],"target_state":[0,0]}' \
	--output summary
```

Phase 2.3 example (2-layer neural training descriptor):

```bash
python -m pirtm transpile \
	--type computation \
	--input examples/transpile_two_layer_nn.json \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 13 \
	--emission-policy pass_through \
	--output summary
```

Quick verify (writes output to `examples/transpile_result.json`): `python -m pirtm transpile --type computation --input examples/transpile_computation.json --prime-index 7919 --identity-commitment 0xabc123 --dim 3 --emission-policy pass_through --output json --output-file examples/transpile_result.json`

Quick verify, two_layer_nn (writes output to `examples/transpile_two_layer_nn_result.json`): `python -m pirtm transpile --type computation --input examples/transpile_two_layer_nn.json --prime-index 7919 --identity-commitment 0xabc123 --dim 13 --emission-policy pass_through --output json --output-file examples/transpile_two_layer_nn_result.json`

Data asset example with explicit prime channel mapping (`prime_map`):

```bash
python -m pirtm transpile \
	--type data_asset \
	--input README.md \
	--prime-index 7919 \
	--identity-commitment 0xabc123 \
	--dim 8 \
	--metadata '{"prime_map":[2,3,5,7]}' \
	--output summary
```

- Release/build automation via `Makefile`:

```bash
make build        # build sdist/wheel
make sbom         # generate SPDX SBOM (requires syft)
make sign         # sign artifacts (requires cosign)
make verify       # verify signatures (requires cosign)
make reproduce    # emit SHA256 manifest for reproducibility
```

## License

MIT (code). The mathematical foundations — contractive recurrence, PETC prime ordering, CSL operators, and contraction safety certificates — are part of the Constitutional Core dedicated to the public domain. See [PATENT PLEDGE.md](PATENT%20PLEDGE.md) for the full ΛProof Open Mathematical Foundation Pledge.
