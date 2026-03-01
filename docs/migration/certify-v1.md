# certify.py v1 Migration Guide

`certify.py` is now a façade over the `pirtm.ace` implementation.

## Return-type strategy

- `ace_certificate(...)` returns `pirtm.ace.types.AceCertificate` (default path).
- `ace_certificate_v2(...)` is a deprecated compatibility alias and returns `pirtm.ace.types.AceCertificate`.
- `legacy_ace_certificate(...)` is deprecated and returns legacy `pirtm.types.Certificate`.

Compatibility window:

- `v0.1.x` keeps legacy compatibility through `legacy_ace_certificate(...)`.
- New and migrated callsites should use `ace_certificate(...)` and `AceCertificate` typing.

## Field compatibility

The legacy fields are preserved across both paths:

- `certified`
- `margin`
- `tail_bound`
- `details["max_q"|"target"|"steps"]`

The ACE-native path additionally exposes:

- `level`
- `lipschitz_upper`
- `gap_lb`
- `contraction_rate`
- `budget_used`
- `tau`
- `delta`

## Recommended migration

1. Update type annotations from `Certificate` to `AceCertificate` where `ace_certificate(...)` is used.
2. Replace any `ace_certificate_v2(...)` usage with `ace_certificate(...)`.
3. Use `legacy_ace_certificate(...)` only where a strict legacy `Certificate` instance is required.
4. Remove uses of `legacy_ace_certificate(...)` as downstream consumers migrate.

## Compatibility guarantees

- Legacy fields remain stable across both paths: `certified`, `margin`, `tail_bound`.
- Legacy details compatibility keys remain present on ACE-native certificates: `max_q`, `target`, `steps`.
- Legacy conversion includes ACE-level provenance under `details["ace_level"]` for mixed-mode auditing.
