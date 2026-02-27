# Release Checklist

## Pre-release

- [ ] Ensure branch is up to date with `main`
- [ ] Run `ruff check src tests`
- [ ] Run `mypy src`
- [ ] Run `pytest -q`
- [ ] Run `pirtm-conformance --profile all --output text`
- [ ] Confirm `CHANGELOG.md` has release notes under `Unreleased`

## Versioning

- [ ] Bump version: `python scripts/bump_version.py patch`
- [ ] Verify version changed in `pyproject.toml` and `src/pirtm/__init__.py`
- [ ] Commit version + changelog updates
- [ ] Create tag (`git tag vX.Y.Z`) or run with `--tag`

## Build and Integrity

- [ ] Build: `python -m build`
- [ ] Check artifacts: `python -m twine check dist/*`
- [ ] Generate SBOM: `make sbom`
- [ ] (Optional) Sign artifacts: `make sign`
- [ ] (Optional) Verify signatures: `make verify`

## Publish

- [ ] Push commits and tags
- [ ] Confirm `Release` workflow succeeds
- [ ] Confirm package appears on PyPI
- [ ] Confirm GitHub release assets are attached

## Post-release

- [ ] Create next `Unreleased` changelog section
- [ ] Announce release with highlights and migration notes
