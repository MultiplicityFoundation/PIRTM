# ADR-005: ADR Process + Directory Layout

> **Tooling-ADR-000** (this document)  
> **Title**: Establish ADR governance, MADR template, and Tooling repository structure  
> **Status**: Accepted  
> **Date**: 2026-03-10  
> **Authors**: PIRTM Governance Team  
> **Spec Reference**: [PIRTM ADR-004: MLIR Dialect](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)

---

## Problem Statement

The Phase Mirror project spans two repositories (PIRTM and Tooling) with different decision scopes:

- **Semantic decisions** (type system, passes, coupling model) live in PIRTM's ADR-004 and are global truth
- **Implementation decisions** (build, CI, test structure, file layout) are local to Tooling and must not redefine semantics

Currently, no formal process separates these concerns. This creates two risks:

1. **Spec Drift**: Tooling changes to diagnostic strings or pass ordering silently contradict ADR-004
2. **Lost Context**: Implementation decisions lack clear rationale, making future changes harder

## Solution

Establish a two-tier ADR structure with explicit "spec reference" headers:

### Tier 1: Normative Spec (PIRTM Repo)
- **ADR-004**: MLIR dialect, types, passes, coupling semantics, inspect/audit layers
- **Rule**: No Tooling ADR may redefine or contradict these decisions

### Tier 2: Implementation (Tooling Repo)
- **Tooling-ADR-NNN** (published as ADR-005+): Build gates, CI workflows, file layout, test fixtures, migration tooling
- **Rule**: Every Tooling ADR must include `Spec Reference: [PIRTM ADR-004]` header and may reference but not redefine semantics

### Directory & File Structure

```
Tooling/
├── docs/adr/
│   ├── README.md                           # This process document
│   ├── MADR-TEMPLATE.md                    # Standard template for all future ADRs
│   ├── ADR-005-adr-process-layout.md      # (This file)
│   ├── ADR-006-dialect-type-layer-gate.md # Day 0–3 gate (transpile-time basic types)
│   ├── ADR-007-prime-mod-migration.md     # Day 0–14 migration + shim protocol
│   └── ADR-008-linker-coupling-gates.md   # Day 14–16 link-time coupling resolution
├── docs/migration/
│   └── prime-to-mod-rename.md             # Structured audit/migration guide
├── pirtm/
│   ├── dialect/
│   │   ├── pirtm.td                       # TableGen definitions
│   │   └── pirtm_types.cpp                # Verifier helpers, Miller-Rabin, isprime()
│   ├── transpiler/
│   │   ├── mlir_emitter.py                # .mlir → .pirtm.bc with !pirtm_proof
│   │   └── pirtm_link.py                  # name-resolution, commitment-crosscheck, matrix
│   ├── spectral_gov.py                    # SpectralGovernor (frozen until ADR-004 merges)
│   ├── tests/
│   │   ├── pirtm-types-basic.mlir         # Day 0–3 acceptance test (four cases)
│   │   ├── commitment-collision-test.py   # Day 14–16 coupling validation
│   │   └── link-test-pair.py              # r=0.7 (pass), r=1.1 (fail) acceptance tests
│   └── examples/                          # Round-trip test cases for Day 7–14
```

### ADR Numbering & Naming

1. **Numbering**: ADR-005, ADR-006, ADR-007, …  (Tooling repo sequence)
2. **Naming convention**: `ADR-XXX-slug-describing-decision.md`
3. **Examples**:
   - `ADR-005-adr-process-layout.md`
   - `ADR-006-dialect-type-layer-gate.md`
   - `ADR-007-prime-mod-migration.md`

### MADR Template (All Future ADRs)

Every new Tooling ADR **must** follow this structure:

```markdown
# ADR-NNN: <Decision Title>

> **Status**: [Proposed|Accepted|Deprecated]  
> **Date**: YYYY-MM-DD  
> **Authors**: <names>  
> **Spec Reference**: [PIRTM ADR-004](link) | [PIRTM Spec](link)

---

## Problem Statement
Description of the problem this ADR solves.

## Solution
<Concise explanation of the chosen approach>

## Consequences

### Positive
- Benefit 1
- Benefit 2

### Negative
- Risk 1
- Risk 2

## Alternatives Considered
- Option A: <why rejected>
- Option B: <why rejected>

## Rationale
Why this solution is correct and sustainable.

## Acceptance Criteria
Measurable tests/gates that validate this ADR.

## References
- Related ADRs
- Spec links
```

### Spec vs. Implementation Rule

| Category | Owner | May Define | Must Not Redefine |
| :--- | :--- | :--- | :--- |
| Type system (kinds, types, mod=) | PIRTM ADR-004 | Semantics, syntax | — |
| Passes (contractivity-check, spectral-small-gain) | PIRTM ADR-004 | Phase, ordering, inputs/outputs | — |
| Coupling schema (session_graph, coupling.json) | PIRTM ADR-004 | Structure, resolution semantics | — |
| Inspect/audit (pirtm inspect output) | PIRTM ADR-004 | Required lines, audit chain | — |
| **Tooling ADRs** | Tooling repo | Build system, CI gates, file layout, test fixtures, diagnostic error strings | Type semantics, pass ordering, coupling semantics |

**Exception for Diagnostic Strings**: Error messages emitted by verifiers are **spec-stable API**. If a Tooling change requires a new diagnostic string, treat it as a spec amendment:
1. Propose the new string in a comment at the top of the Tooling ADR
2. Cross-reference the proposed amendment number in PIRTM ADR-004
3. Wait for PIRTM spec approval before merging

### Escalation Protocol

If a task conflicts with an ADR or L0 invariant:

```
CONFLICT: <one sentence naming the constraint>
TASK REQUESTED: <what was asked>
OPTIONS:
  A. <spec-compatible path>
  B. <spec-compatible path>
WAITING FOR CONFIRMATION.
```

## Consequences

### Positive
- **Single Semantic Truth**: ADR-004 is the only source of truth for MLIR dialect design; no silent drift
- **Transparent Coupling**: "Spec Reference" headers make it obvious which decisions are locked vs. local
- **Reusable Process**: Future projects can adopt the same Tier 1 + Tier 2 structure
- **Clearer Escalation**: Conflicts are surfaced early with explicit options

### Negative
- **Process Overhead**: Every Tooling ADR must include header boilerplate and reference ADR-004
- **Slower Iteration**: New diagnostic strings require PIRTM spec approval (typically 1–2 days)

## Alternatives Considered

1. **Single ADR Document**: Keep all decisions (PIRTM + Tooling) in one file
   - **Rejected**: No separation of concerns; semantic decisions drowend in build plumbing

2. **Tooling ADRs Redefine Semantics**: Allow Tooling to override PIRTM ADR-004
   - **Rejected**: Violates the "single source of truth" principle; creates spec contradictions

3. **Informal Process**: Use GitHub comments instead of formal ADRs
   - **Rejected**: No durable record; context is lost; no structured decision log

## Rationale

The two-tier structure preserves **one semantic truth** while allowing **fast local iteration**. PIRTM owns what the system is; Tooling owns how we build it. The "Spec Reference" header makes the boundary explicit, preventing accidental redefinitions. Diagnostic string escalation is the only exception—it's a rare case that warrants spec-level discussion.

## Acceptance Criteria

- [ ] This ADR (ADR-005) is merged and referenced in `docs/adr/README.md`
- [ ] `MADR-TEMPLATE.md` exists in `docs/adr/` with the above structure
- [ ] ADR-006, ADR-007, ADR-008 are drafted and include "Spec Reference: PIRTM ADR-004" headers
- [ ] The directory structure under `pirtm/` matches the layout in this ADR
- [ ] All team members acknowledge the Tier 1 + Tier 2 boundary in weekly sync

