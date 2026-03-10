# ETP Pass 3 — ADR-012 (Docs + Tests)

- Type: execution PR pass
- Date: 2026-03-01
- Scope: third concrete implementation slice from accepted-candidate sequence

## Included ADRs

1. ADR-012 — Envelope validation and TRL claim discipline

## Deliverables

- TRL code-first evidence expanded:
  - Explicit tests added for `CertLevel` → TRL mapping.
- Commitment-vs-measurement payload separation expanded:
  - L3 details include runtime clamp evidence alongside designed clamp commitment.
  - L4 details include runtime perturbation evidence alongside designed perturbation commitment.
- ADR record updated with pass-specific execution notes.

## Validation Commands

```bash
pytest -q tests/test_ace_trl_metadata.py tests/test_ace_protocol.py tests/test_ace_protocol_injection.py
```

## Exit Criteria

- All targeted tests pass.
- No regression in existing ACE protocol behavior.
- ADR-012 candidate text and test evidence remain consistent.
