# ETP Pass 4 — ADR-010 (Docs + Tests)

- Type: execution PR pass
- Date: 2026-03-01
- Scope: fourth concrete implementation slice from accepted-candidate sequence

## Included ADRs

1. ADR-010 — ACE/PETC development blueprint (release-aligned)

## Deliverables

- Protocol composition determinism implemented:
  - Batch representative selection is capability-first (highest feasible ACE level).
  - `q` remains deterministic tie-breaker within the same feasible level.
- Test evidence expanded:
  - Capability-priority dispatch assertion for mixed-feasibility batches.
  - Same-level tie-break assertion pinned to `q` ordering.
- ADR record updated with pass-specific execution notes.

## Validation Commands

```bash
pytest -q tests/test_ace_protocol.py tests/test_ace_protocol_injection.py tests/test_ace_trl_metadata.py
```

## Exit Criteria

- All targeted tests pass.
- No regression in existing ACE protocol behavior.
- ADR-010 candidate text and protocol composition tests remain consistent.
