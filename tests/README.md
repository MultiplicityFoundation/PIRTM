## Test Suite Guide

This directory contains release-gated tests for the `pirtm` package.

### Quick Commands

- Full suite:

```bash
python -m pytest -q
```

- Coverage run (mirrors CI intent):

```bash
python -m pytest --cov=pirtm --cov-report=term-missing -v
```

- Targeted transpiler + ACE critical suites:

```bash
python -m pytest -v \
	tests/test_cli_transpile.py \
	tests/test_transpiler.py \
	tests/test_ace_protocol.py \
	tests/test_ace_protocol_injection.py \
	tests/test_ace_matrix_immutability.py \
	tests/test_simulations_modernized.py
```

- Local release-gate checks:

```bash
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src/pirtm
python -m pytest -q
```

### Marker Policy

- The suite runs with `--strict-markers` (configured in `pyproject.toml`).
- Add new markers only with matching registration in project pytest configuration.

### Runtime Expectations

- On current `v0.1.0` baseline, full local suite is expected to pass with no failures.
- Deprecation warnings from `pirtm._legacy` are expected until planned removal in `v0.3.0`.

