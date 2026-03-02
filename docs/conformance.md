# Conformance Test Guide

This document summarizes conformance-oriented checks aligned with the PIRTM
language specification.

## Purpose

Conformance tests verify that runtime behavior matches normative invariants and
API contracts from `docs/PIRTM_LANGUAGE_SPEC.md`.

## Test modules

Current conformance coverage under `tests/conformance/`:

- `test_spec_compliance.py`
  - §5 certificate type alignment (`contraction_certificate`, `ace_certificate`)
- `test_emission_gate_policies.py`
  - §8 emission-gate policy behavior and CSL-gated composition
- `test_witness_dual_hash.py`
  - §9 witness dual-hash and single-hash schema behavior
- `test_l0_invariants.py`
  - §11 L0 invariants for contraction typing and fail-closed emission

## Running conformance tests

Run all conformance modules:

```bash
python -m pytest -q tests/conformance/
```

Run a single module:

```bash
python -m pytest -q tests/conformance/test_spec_compliance.py
```

## Scope notes

- Conformance tests complement unit tests and integration tests; they do not
  replace them.
- Assertions are written against current public runtime APIs in `src/pirtm`.
- Legacy/deprecated internals under `pirtm._legacy` are not used for conformance
  pass criteria.

## Release gate usage

For release candidates, run:

1. `python -m pytest -q tests/conformance/`
2. `python -m mypy`
3. `python -m ruff check .`

Conformance status should be evaluated alongside migration docs and changelog
entries for the target release.
