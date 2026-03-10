# MADR-TEMPLATE.md

Copy this template for every new Tooling ADR. Fill in each section with concrete details.

---

# ADR-NNN: <Title of Decision>

> **Status**: [Proposed|Accepted|Deprecated]  
> **Date**: YYYY-MM-DD  
> **Authors**: Your Name(s)  
> **Spec Reference**: [PIRTM ADR-004](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)

---

## Problem Statement

**What problem does this ADR solve?**

Write 2–3 sentences describing the problem, the context, and why it matters.

*Example*:
> Currently, the transpiler emits MLIR without verifying type coherence at module boundaries. This causes silent coupling errors to slip through transpile time, only surfacing during the linking phase. This delays error feedback and complicates debugging.

---

## Solution

**What is the chosen approach?**

Describe the solution concisely. Include:
- Key design decisions
- How it solves the problem
- Any constraints it respects (e.g., "does not violate L0 invariant #3")

*Example*:
> Add a type-coherence pass to the transpiler that runs immediately after parsing. The pass verifies that every `pirtm.module`:
> 1. Carries exactly one `prime_index` (L0 invariant #1)
> 2. Has consistent `op_norm_T` across all uses
> 3. Emits a spec-stable error message if verification fails

---

## Consequences

### Positive

List the benefits of this decision.

- Benefit 1
- Benefit 2
- Benefit 3

### Negative

List the costs, tradeoffs, or new problems introduced.

- Cost 1
- Cost 2

---

## Alternatives Considered

For each alternative, explain **why it was rejected**.

### Alternative A: <Option Name>

**Description**: Brief explanation of the approach.

**Rejection Reason**: Why this was not chosen.

**Tradeoff**: What would have been different.

### Alternative B: <Option Name>

**Description**: Brief explanation of the approach.

**Rejection Reason**: Why this was not chosen.

**Tradeoff**: What would have been different.

---

## Rationale

**Why is this the right decision?**

Explain the reasoning in 2–4 sentences. Reference:
- Spec constraints (PIRTM ADR-004)
- L0 invariants that must be respected
- Performance, complexity, or sustainability tradeoffs

*Example*:
> We chose early verification (transpile time) rather than late verification (link time) to catch type errors as early as possible. This aligns with PIRTM ADR-004's two-phase model: transpile time is phase 1, and must enforce module-level coherence. The cost is a small compile-time overhead, which is acceptable because type coherence is checked once per module.

---

## Acceptance Criteria

**How do we know this ADR is working?**

List testable, measurable conditions that must be satisfied. These become part of the CI gate.

- [ ] Criterion 1 (e.g., "type-coherence pass compiles without warnings")
- [ ] Criterion 2 (e.g., "pirtm-types-basic.mlir runs with `mlir-opt --verify-diagnostics` and passes all four test cases")
- [ ] Criterion 3 (e.g., "error message matches spec-stable string: `mod={mod} is not prime ({factored_form})`")
- [ ] Criterion 4 (e.g., "All examples in `pirtm/examples/` round-trip without error")

---

## References

List related ADRs, spec documents, or GitHub issues.

- [PIRTM ADR-004: MLIR Dialect](https://github.com/MultiplicityFoundation/PIRTM/docs/adr/ADR-004-pirtm-mlir-dialect.md)
- [ADR-005: ADR Process + Directory Layout](./ADR-005-adr-process-layout.md) (this governance structure)
- [GitHub Issue #123](https://github.com/MultiplicityFoundation/Tooling/issues/123) (problem context)

---

## Notes for Reviewers

(Optional) Add any clarifications or discussion points here.

---

## Sign-Off

- [ ] Language Architect (PIRTM spec) approved
- [ ] Tooling Maintainer approved
- [ ] CI/Infra approved (if affects build/gates)

