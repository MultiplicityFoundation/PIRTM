# PIRTM Plans Index

## Active Roadmap (Source of Truth)

- **Active roadmap**: `docs/plans/PIRTM Core Completion.md`
- **Current execution tracks**: `R1` through `R10` under `docs/plans/issue-drafts/`

## Plan Status Map

| Document | Status | Notes |
|---|---|---|
| `PIRTM Core Completion.md` | **Active** | Canonical roadmap for current release and modernization work |
| `issue-drafts/` | **Active** | Actionable execution backlog aligned to active roadmap |
| `PIRTM Transpiler Spec.md` | **Reference** | Living technical spec; implementation may evolve by release track decisions |
| Spectral boundary (`pirtm.spectral_decomp`) | **Active Policy** | Supported public API for `v0.1.x`; `_legacy` spectral paths are transition-only |
| `PIRTM Tier 1 Expansion.md` | **Historical** | Superseded by active roadmap and issue-draft execution model |
| `PIRTM Tier 2 Expansion.md` | **Historical** | Superseded by active roadmap and issue-draft execution model |
| `PIRTM Tier 3 Expansion.md` | **Historical** | Superseded by active roadmap and issue-draft execution model |
| `PIRTM Tier 4 Expansion.md` | **Historical** | Superseded by active roadmap and issue-draft execution model |
| `PIRTM Tier 5 Expansion.md` | **Historical** | Superseded by active roadmap and issue-draft execution model |
| `PIRTM Tier 6 Expansion.md` | **Historical** | Superseded by active roadmap and issue-draft execution model |
| `PIRTM Tier 7 Expansion.md` | **Historical** | Superseded by active roadmap and issue-draft execution model |
| `ADR-000_Thread.md` | **Historical / Exploratory** | Background exploration; not authoritative for release decisions |
| `ADR-006_ETP.md` | **Active / Accepted Candidate** | ACE/PETC modernization sequencing candidate |
| `ADR-007_ETP.md` | **Active / Accepted Candidate** | Design-parameter commitment model candidate |
| `ADR-008_ETP.md` | **Active / Accepted Candidate** | Unified ACE telemetry contract candidate |
| `ADR-009_ETP.md` | **Active / Accepted Candidate** | Certificate type migration candidate |
| `ADR-010_ETP.md` | **Active / Accepted Candidate** | Release-aligned ACE/PETC blueprint candidate |
| `ADR-011_ETP.md` | **Active / Accepted Candidate** | Matrix immutability contract candidate |
| `ADR-012_ETP.md` | **Active / Accepted Candidate** | Envelope validation + TRL discipline candidate |
| `ADR-013_ETP.md` | **Active / Accepted Candidate** | Protocol default injection semantics candidate |

## Support Matrix (Current)

| Subsystem | Status | Stability | Notes |
|---|---|---|---|
| PIRTM core recurrence/certification | Active | Stable for `v0.1.0` scope | Release-gated through CI, conformance, and checklist flows |
| ACE package (`pirtm.ace.*`) | Active | Experimental-to-stabilizing | Covered by targeted critical suites and integration checks |
| Transpiler (`pirtm.transpiler.*`) | Active | Stabilizing | CLI/workflow gates include explicit output-gating behavior |
| Spectral public APIs (`pirtm.spectral_decomp`, `pirtm.spectral_gov`) | Active | Stable for `v0.1.x` | Canonical boundary decision documented in `docs/architecture.md` |
| Legacy surfaces (`pirtm._legacy`) | Active (deprecated) | Transitional | Sunset boundary and timeline tracked in `R4` / `R5` |
