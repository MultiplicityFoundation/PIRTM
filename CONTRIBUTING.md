# Contributing to PIRTM

## Core Principles

- Preserve contractivity and safety invariants.
- Prefer minimal, targeted changes.
- Keep dependencies lean and deterministic.
- Avoid telemetry/network side effects by default.

## Development Setup

```bash
git clone https://github.com/MultiplicityFoundation/PIRTM.git
cd PIRTM
pip install -e ".[dev]"
python -m pytest -q
```

## Commit Conventions

Use conventional commits:

- `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `security`, `ci`

Examples:

- `feat(recurrence): add spectral-safe projector path`
- `fix(certify): correct tail bound for edge instability`

## Pull Requests

- Keep PRs focused and reviewable.
- Include rationale for invariant-sensitive changes.
- Add/adjust tests for every behavior change.
- Release-gate expectations are defined in `docs/release_checklist.md` under “Release Gate Matrix (R8 Canonical)”.
- Ensure local checks pass:

```bash
ruff check src tests
mypy src/pirtm
pytest --cov=pirtm -q
```

## Testing Expectations

- Core (`recurrence`, `projection`, `certify`): target 100% branch coverage.
- Tier 2 (`weights`, `gain`, `csc`): target 95% branch coverage.
- Utility modules (`petc`, `monitor`, `adaptive`): target 90%+.
- Integration tests should exercise complete contractive pipelines.

## Style and Typing

- Use `ruff` for linting and import ordering.
- Keep public functions type-annotated.
- Follow existing module style and naming.

## Security Checklist

- No secrets in code or tests.
- No PII handling.
- No unsolicited outbound network calls.
- Validate numerical edge cases and denial-of-service risks.

## License

- Code: MIT
- Documentation and theory assets: project policy applies.
