<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# lets create an ADR plan for these developments.

Create a small ADR *stack* that keeps ADR-004 as the normative spec, while moving Tooling-specific build/CI/layout decisions into separate “implementation ADRs” that reference ADR-004 rather than duplicating it.

## Central tension

We need to preserve **one** language/governance truth (ADR-004) while still allowing Tooling to evolve build plumbing, CI gates, and file layout without silently editing the spec.  The ADR plan below makes that separation explicit: PIRTM owns “what the system is,” Tooling owns “how we compile/test/enforce it.”

## Levers (owner, metric, horizon)

- Owner: Language Architect; Metric: ADR-004 remains the only place that defines semantics (kinds, passes, two-phase model, coupling schema, inspect/audit layers); Horizon: 7 days.
- Owner: Tooling Maintainer; Metric: Tooling ADRs only define build+test+repo layout and must include “Spec reference: ADR-004” header; Horizon: 7 days.
- Owner: CI/Infra; Metric: one CI workflow enforces the Day-0/Day-3 gates (TableGen compile + `mlir-opt --verify-diagnostics` on the basic types test); Horizon: 14 days.


## ADR plan (minimal set)

1) **Tooling-ADR-000: ADR process + directory layout**
Artifacts: `Tooling/docs/adr/README.md`, MADR template, naming/numbering rules, “spec vs implementation” rule.
2) **Tooling-ADR-001: PIRTM dialect type-layer gate (Day 0–3)**
Scope: `pirtm.td` TypeDefs + `SessionGraphOp` stub, `pirtm_types.cpp` verifier helpers, and `pirtm-types-basic.mlir` as the acceptance test; explicitly references ADR-004’s `mod=` and squarefree/prime constraints.
3) **Tooling-ADR-002: prime→mod migration + shim protocol (Day 0–14)**
Scope: the structured audit/migration doc, the temporary shim (`PrimeChannel.prime → property over .mod`), and the exact merge gate grep commands; explicitly references ADR-004’s atomic Day-14 rename requirement.
4) **Tooling-ADR-003: Linker inputs + coupling resolution gates (Day 14–16)**
Scope: `coupling.json` schema, the three-pass resolution pipeline, commitment-collision test, and where `pirtm_link.py` lives; references ADR-004’s link-time `session_graph` semantics.

## Artifacts to update first

- PIRTM: add a short note at the top of ADR-004: “Implementation ADRs live in Tooling; they may not redefine semantics.”
- Tooling: create `docs/adr/` + `Tooling-ADR-000` and land the three Day-0 artifacts alongside `Tooling-ADR-001` immediately.

Precision question: Should Tooling ADRs be allowed to introduce *new verifier diagnostics strings* (for the `.mlir` expected-error matching), or must those diagnostics be treated as spec-stable API and therefore require a PIRTM ADR update to change?
<span style="display:none">[^1][^10][^11][^12][^13][^14][^15][^16][^17][^18][^19][^2][^20][^21][^22][^23][^24][^25][^26][^27][^28][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: https://github.com/mskilab-org/multiplicity

[^2]: https://github.com/mgeeky/ProtectMyTooling

[^3]: https://github.com/mims-harvard/ToolUniverse

[^4]: https://github.com/arcee-ai/mergekit

[^5]: https://github.com/alassek/multiplicity

[^6]: https://github.com/multiply-org/multiply-core/wiki/Development-Process/65066139a55263b2fdd9cbfa4e38388e7d7f4d71

[^7]: https://github.com/charliemarx/pmtools

[^8]: https://github.com/multiply-org/multiply-orchestration/blob/master/README.md

[^9]: https://github.com/rustdesk/rustdesk/wiki/FAQ

[^10]: https://github.com/alibaba/higress

[^11]: https://github.com/web-infra-dev/rslib

[^12]: https://github.com/TablePlus/TablePlus

[^13]: https://github.com/coreinfrastructure/best-practices-badge

[^14]: https://github.com/tylerjwatson/Multiplicity/blob/master/LICENSE

[^15]: https://github.com/golang/go/issues/32017

[^16]: https://github.com/socialfoundations/mono-multi

[^17]: https://github.com/volatilityfoundation

[^18]: https://github.com/orgs/volatilityfoundation/repositories

[^19]: https://github.com/realpython/codetiming

[^20]: https://github.com/JWatsonDaniels/multitarget-multiplicity

[^21]: https://github.com/volatilityfoundation/volatility/wiki/command-reference

[^22]: https://github.com/golemparts/rppal

[^23]: https://www.sciencedirect.com/science/article/pii/S2352711018301833

[^24]: https://github.com/stalwartlabs/mail-parser

[^25]: https://gftn.co/hubfs/multiplicity and convergence in the digital assets ecosystem_final.pdf

[^26]: https://github.com/chatmail/async-imap

[^27]: https://dl.acm.org/doi/10.1145/3677173

[^28]: https://www.repository.law.indiana.edu/cgi/viewcontent.cgi?article=11580\&context=ilj

