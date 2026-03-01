# R6: Migrate simulations off `_legacy` (or classify explicitly)

- **Type**: Feature request
- **Labels**: `enhancement`, `legacy`, `simulations`
- **Track**: C (Simulation Modernization)
- **Size**: M
- **Depends on**: R4

## Summary

Modernize simulation modules currently importing `pirtm._legacy`, or explicitly classify and isolate simulations that remain legacy-backed.

## Motivation

Simulation paths still coupled to legacy APIs create drift against the modern contractive core and complicate future removals.

## Acceptance Criteria

- [ ] Inventory of simulation modules and import paths is documented.
- [ ] Each simulation is either migrated to modern APIs or explicitly marked as legacy.
- [ ] Legacy-classified simulations are isolated and documented as non-core.
- [ ] Modernized simulations run successfully with current package APIs.

## Implementation Checklist

- [ ] Audit `src/pirtm/simulations/*.py` legacy imports.
- [ ] Replace with core APIs (`recurrence`, `qari`, `gate`, `certify`) where feasible.
- [ ] Add clear headers/docs for any simulation intentionally left legacy.
- [ ] Update examples/docs references to modernized simulation entry points.

## Out of Scope

- Comprehensive test hardening for simulations (handled in `R7`).
