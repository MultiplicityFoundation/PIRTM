# Requirements Matrix

This project uses a minimal runtime dependency set and layered extras for development and release work.

## Python Version

- Required Python: `>=3.11`

## Runtime Requirements

Defined in `pyproject.toml` under `[project.dependencies]`:

- `numpy>=1.24`

Install runtime only:

```bash
pip install -e .
```

## Development Requirements

Defined in `pyproject.toml` under `[project.optional-dependencies].dev`:

- `pytest>=8.0`
- `pytest-cov>=5.0`
- `ruff>=0.4`
- `mypy>=1.10`

Install dev extras:

```bash
pip install -e ".[dev]"
```

## Legacy Extras

Defined in `[project.optional-dependencies].legacy`:

- `sympy>=1.12`
- `matplotlib>=3.7`

Install legacy extras:

```bash
pip install -e ".[legacy]"
```

## Release Requirements (Python)

Defined in `[project.optional-dependencies].release`:

- `build>=1.2`
- `twine>=5.0`

Install release extras:

```bash
pip install -e ".[release]"
```

## Combined Extras

Defined in `[project.optional-dependencies].all`:

```bash
pip install -e ".[all]"
```

## Optional Release Tooling (System Binaries)

Used by `Makefile` targets for supply-chain tasks:

- `syft` for `make sbom`
- `cosign` for `make sign` and `make verify`

These are optional for standard build/test flow and required only when running those optional integrity targets.
