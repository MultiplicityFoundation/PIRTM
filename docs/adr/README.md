# Architecture Decision Records (ADRs)

This directory contains architecture decisions for the PIRTM Tooling repository. These records document the **implementation** decisions that support the canonical semantic specification in `MultiplicityFoundation/PIRTM`.

## Quick Reference

| ADR | Title | Scope | Status |
| :-- | :-- | :-- | :-- |
| [ADR-005](./ADR-005-adr-process-layout.md) | ADR Process + Directory Layout | Governance, file structure | Accepted |
| [ADR-006](./ADR-006-dialect-type-layer-gate.md) | PIRTM Dialect Type-Layer Gate (Day 0–3) | TableGen, verifier, basic types test | Proposed + Implemented |
| [ADR-007](./ADR-007-prime-mod-migration.md) | Prime → Mod Migration + Shim Protocol (Day 0–14) | Type rename, compatibility shim, round-trip tests | Proposed |
| [ADR-008](./ADR-008-linker-coupling-gates.md) | Linker Inputs + Coupling Resolution (Day 14–16) | Coupling.json, three-pass linker, spectral gates | Proposed |
| [ADR-009](./ADR-009-digital-vin-and-glass-box-identity.md) | Digital VIN + Glass-Box Identity Protocol (Day 30+) | Hash tree composition, PGIF serialization, `pirtm vin` CLI | Proposed |

---

## Two-Tier ADR Structure

### Tier 1: Normative Specification (PIRTM Repo)

**PIRTM ADR-004: MLIR Dialect and Compositional Hash Identity** defines the **semantic truth** for:
- Type system (kinds, types, `mod=` modulus, prime/composite constraints)
- Compiler passes (order, inputs, outputs)
- Coupling schema and session graph semantics
- Inspect/audit layer specification
- Four-level hash composition (component → subsystem → engine → chassis → VIN)
- Glass-box identity and proof-of-correctness principles

**Reference**: [Tooling ADR-004.md](./ADR-004.md) provides architectural context and is available for review, but it links to the authoritative spec in the PIRTM repository.

**Rule**: No Tooling ADR may redefine or contradict these decisions.

### Tier 2: Implementation (This Repo)

**Tooling ADRs** (ADR-005+) define the **local decisions** for:
- Build system and CI gates
- File organization and naming
- Test fixtures and acceptance criteria
- Migration tooling and shims

**Rule**: Every Tooling ADR must include a "Spec Reference: PIRTM ADR-004" header and may reference but not redefine semantics.

---

## How to Write a Tooling ADR

1. **Copy the template** from [MADR-TEMPLATE.md](./MADR-TEMPLATE.md)
2. **Name the file** as `ADR-NNN-slug-for-decision.md`
3. **Add the header** at the top:
   ```markdown
   > **Status**: [Proposed|Accepted|Deprecated]  
   > **Date**: YYYY-MM-DD  
   > **Authors**: <names>  
   > **Spec Reference**: [PIRTM ADR-004](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)
   ```
4. **Fill each section** following the template structure
5. **Define acceptance criteria** that are testable and measurable
6. **Submit for review** with reference to any related PIRTM decisions

---

## Spec vs. Implementation Boundary

When deciding whether a change is a spec amendment or an implementation decision:

| Decision | Belongs In | May Change | Implications |
| :--- | :--- | :--- | :--- |
| `!pirtm.cert` is always prime | PIRTM ADR-004 | Never | Affects all Tooling code depending on cert structure |
| Passes run in order: contractivity → spectral-small-gain | PIRTM ADR-004 | Never | Affects transpiler and linker pipeline |
| Error message text for "mod is not prime" | PIRTM ADR-004 | Only via spec amendment | Must be coordinated across both repos |
| File location of pirtm.td | Tooling ADR | Yes | Local to Tooling repo |
| Which Python test framework we use | Tooling ADR | Yes | Local to Tooling repo |

### Exception: Diagnostic Strings

Error messages from verifiers are **spec-stable API**—they are matched by `.mlir` test files using expected-error directives. If a Tooling change requires a new diagnostic string:

1. **Propose** the new string in your Tooling ADR
2. **Cross-reference** the proposed string with PIRTM ADR-004
3. **Wait** for PIRTM spec approval before merging

Example:
```
PROPOSED NEW DIAGNOSTIC:
"mod={mod} is composite (factors: {factorization})"

RATIONALE: Provides users with explicit factorization for debugging.

APPROVAL: Awaiting PIRTM ADR-004 amendment [PENDING].
```

---

## Escalation: Naming a Conflict

If a task conflicts with an ADR or L0 invariant, **stop and escalate** using this format:

```
CONFLICT: Invariant #3: !pirtm.cert must be prime-typed; task requests composite cert support.
TASK REQUESTED: "Add generic-cert type to handle multi-modal proofs"
OPTIONS:
  A. Add !pirtm.generic_cert in PIRTM ADR-004 (spec change), then implement in Tooling
  B. Decompose multi-modal proof into separate prime certs and compose externally
WAITING FOR CONFIRMATION.
```

Post the conflict as a comment or GitHub issue and wait for a spec-level decision.

---

## Sequencing Gates

Do not work past a gate before it passes. Each gate is a measurable acceptance test:

| Gate | Deadline | Test | Spec Reference |
| :-- | :-- | :-- | :-- |
| **Day 0–3** | Mar 13 | `mlir-opt --verify-diagnostics pirtm-types-basic.mlir` passes all four test cases | [ADR-006](./ADR-006-dialect-type-layer-gate.md) |
| **Day 3–7** | Mar 17 | Coprime merge passes; non-coprime emits the specified diagnostic | [ADR-006](./ADR-006-dialect-type-layer-gate.md) |
| **Day 7–14** | Mar 24 | All `examples/` round-trip via `mlir_emitter.py --output mlir` | [ADR-007](./ADR-007-prime-mod-migration.md) |
| **Day 14** | Mar 24 | `pirtm inspect basic.pirtm.bc \| grep "contractivity_check: PASS"` | [ADR-007](./ADR-007-prime-mod-migration.md) |
| **Day 14–16** | Mar 26 | Commitment-collision test passes | [ADR-008](./ADR-008-linker-coupling-gates.md) |
| **Day 30** | Apr 9 | r=0.7 link passes; r=1.1 link fails with diagnostic | [ADR-008](./ADR-008-linker-coupling-gates.md) |
| **Day 90** | May 10 | `pirtm.step` ≥10× NumPy on 512-dim tensor | Backend Abstraction |
| **Day 7–14** | Mar 24 | All `examples/` round-trip via `mlir_emitter.py --output mlir` | ADR-007 |
| **Day 14** | Mar 24 | `pirtm inspect basic.pirtm.bc \| grep "contractivity_check: PASS"` | ADR-007 |
| **Day 14–16** | Mar 26 | Commitment-collision test passes | ADR-008 |
| **Day 30** | Apr 9 | r=0.7 link passes; r=1.1 link fails with diagnostic | ADR-008 |
| **Day 90** | May 10 | `pirtm.step` ≥10× NumPy on 512-dim tensor | Backend ABstraction |

---

## L0 Invariants (Non-Negotiable)

These constraints are locked in PIRTM ADR-004 and must never be violated:

1. `pirtm.module` carries exactly one `prime_index`, one `epsilon`, one `op_norm_T`. No `epsilon_map`. No multi-prime modules.
2. `contractivity-check` runs at transpile time. `spectral-small-gain` runs at link time. No pass runs out of this order.
3. `!pirtm.cert` is always prime-typed. There is no composite cert.
4. `pirtm.session_graph.gain_matrix` is never a transpile-time attribute. Must be `#pirtm.unresolved_coupling` at transpile time.
5. Composite `mod=` values must be squarefree (μ(mod) ≠ 0). `mod=` on atomic types must pass Miller-Rabin.
6. Human names in `coupling.json` do not survive into IR. `pirtm.session_graph` is indexed by `prime_index` only.
7. The `pirtm inspect` output must always include `Audit Chain: NOT EMBEDDED — retrieve via pirtm audit <trace.log>`. This line is not optional.

---

## Related Documents

- **PIRTM ADR-004**: [MLIR Dialect Specification](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md) — the canonical spec
- **Governance-Truth.md**: Initial proposal for two-tier ADR structure
- **Migration Guide**: [docs/migration/prime-to-mod-rename.md](../migration/prime-to-mod-rename.md) — detailed rename + shim protocol

---

## Template & Conventions

See [MADR-TEMPLATE.md](./MADR-TEMPLATE.md) for the standard MADR structure.

**Naming Convention**: `ADR-NNN-slug-describing-decision.md`
- Example: `ADR-005-adr-process-layout.md`
- Use kebab-case for the slug
- Start with a zero-padded number (ADR-005, not ADR-5)

**Status Values**:
- `Proposed`: Under discussion; not yet approved
- `Accepted`: Approved; ready to implement
- `Deprecated`: Superseded by a newer ADR

**Header Template**:
```markdown
> **Status**: Accepted  
> **Date**: 2026-03-10  
> **Authors**: Your Name  
> **Spec Reference**: [PIRTM ADR-004](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)
```

---

## Questions?

Contact the Governance Team or post in the Tooling repo issues.
