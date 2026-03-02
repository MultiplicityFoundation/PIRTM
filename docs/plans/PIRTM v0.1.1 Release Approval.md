# PIRTM v0.1.1 Release Approval

**Status:** ✅ **GO FOR RELEASE**

**Date:** March 2, 2026, 6:36 PM EST
**Commit:** Ready for tag
**Target:** PyPI + GitHub Release

***

## Release Gates: ALL GREEN ✅

### Gate 1: Conformance Suite

**Status:** ✅ **PASS** (17/17)
**Evidence:** All conformance tests passing in codespace
**Coverage:** §5 (Certificates), §8 (Emission Gates), §9 (Witness), §11 (L0 Invariants)

### Gate 2: Full Test Suite

**Status:** ✅ **PASS** (207/207)
**Evidence:** No failures, comprehensive coverage
**Note:** 4 deprecation warnings from `pirtm._legacy` (expected, non-blocking)

### Gate 3: Type Safety

**Status:** ✅ **PASS**
**Evidence:** `mypy` clean, `ruff` clean
**Type coverage:** Full static analysis passing

### Gate 4: Conformance CLI

**Status:** ✅ **PASS**
**Command:** `pirtm-conformance --profile all --output text`
**Result:** Core + integrity profiles passing

### Gate 5: Documentation

**Status:** ✅ **COMPLETE**
**Delivered:**

- Certificate API clarification (`contraction_certificate()` vs `ace_certificate()`)
- PETC coverage/validation CLI docs
- Conformance test documentation
- Certificate usage examples

***

## Breaking Changes Assessment

**Breaking changes:** ✅ **NONE**

All v0.1.0 code continues to work:

```python
# v0.1.0 code (still works)
from pirtm import ace_certificate
cert = ace_certificate(info)

# v0.1.1 recommended (new)
from pirtm import contraction_certificate
cert = contraction_certificate(info)
```

Backward compatibility maintained via function routing.

***

## Known Issues (Non-Blocking)

### 1. Legacy Import Warnings

**Severity:** Low (transitional)
**Count:** 4 deprecation warnings
**Source:** `pirtm._legacy` import paths
**Impact:** User-visible warnings in logs
**Mitigation:** Expected for transitional release, removal planned for v0.2.0
**Action:** Document in release notes

### 2. Spec Alignment (§5)

**Severity:** Low (documentation)
**Status:** Implementation extends spec (not contradicts)
**Details:** Certificate has additional fields beyond minimal spec
**Impact:** None (implementation richer than spec minimum)
**Action:** Note in CHANGELOG as enhancement

***

## Release Artifacts Checklist

### Pre-Release

- ✅ All tests passing (207/207)
- ✅ Conformance suite passing (17/17)
- ✅ Type checks clean (mypy, ruff)
- ✅ Conformance CLI validated
- ✅ Documentation updated
- ✅ CHANGELOG.md updated
- ✅ Migration guide written (`docs/migration/v0.1.1.md`)


### Release Process

- ⏳ Tag commit: `git tag v0.1.1`
- ⏳ Build: `make build`
- ⏳ Sign: `make sign` (if available)
- ⏳ SBOM: `make sbom` (if syft available)
- ⏳ Verify: `make verify`
- ⏳ Upload: `python -m twine upload dist/*`
- ⏳ GitHub Release created
- ⏳ Announcement posted

***

## GitHub Release Description

**Copy-ready markdown:**

```markdown
# PIRTM v0.1.1 — API Clarity & Conformance Hardening

## Overview

PIRTM v0.1.1 focuses on **API clarity**, **conformance hardening**, and **release-readiness**.

This release introduces a clearer certificate entrypoint ([`contraction_certificate()`](https://github.com/MultiplicityFoundation/PIRTM/blob/v0.1.1/docs/api/certify.md)) while keeping ACE diagnostics available via [`ace_certificate()`](https://github.com/MultiplicityFoundation/PIRTM/blob/v0.1.1/docs/api/certify.md), expands conformance coverage for §5 (Certificates), §8 (Emission Gates), §9 (Witness Language), and §11 (L0 Invariants), and formalizes PETC coverage/validation usage in docs and CLI guidance.

## ✅ Release Gates

All release gates are **GREEN**:
- ✅ Full conformance suite (17/17 passing)
- ✅ Full pytest suite (207 passed, 0 failures)
- ✅ Type safety (mypy clean, ruff clean)
- ✅ Conformance CLI (`pirtm-conformance --profile all` passing)

## 🎯 Key Changes

### API Clarification
**New primary API:** `contraction_certificate(info)` for simple ML0-003 validation  
**Advanced diagnostics:** `ace_certificate(info)` for multi-step aggregate metrics  
**Backward compatible:** All v0.1.0 code continues to work

```python
# Simple validation (recommended)
from pirtm import contraction_certificate
cert = contraction_certificate(info)
if cert.certified:
    print("✓ ML0-003 satisfied")

# Advanced ACE diagnostics
from pirtm import ace_certificate
ace = ace_certificate(info)
print(f"q_max={ace.q_max:.4f}, margin={ace.margin:.4f}")
```


### PETC Coverage Implementation

New CLI tools for PETC chain validation (§7.2):

```bash
# Compute coverage ρ(C,[a,b])
pirtm petc coverage --chain chain.json --range 100-200

# Validate chain invariants
pirtm petc validate --chain chain.json --max-gap 100 --min-coverage 0.8
```


### Conformance Test Suite

Comprehensive conformance tests for PIRTM Language Spec v1.0:

- **§5:** Certificate types and structure
- **§8:** Emission gate policy enforcement
- **§9:** Witness language (single-hash and dual-hash modes)
- **§11:** L0 invariant validation

Run via: `pytest tests/conformance/ -v`

### Documentation

- **API Reference:** Complete documentation for certificate APIs
- **Migration Guide:** `docs/migration/v0.1.1.md`
- **Examples:** `examples/certificate_usage.py` with end-to-end usage patterns
- **Conformance Docs:** Test coverage for spec compliance


## 🔄 Migration from v0.1.0

**No breaking changes.** All v0.1.0 code works as-is.

**Recommended updates:**

```python
# OLD (still works, but prefer new API)
from pirtm import ace_certificate
cert = ace_certificate(info)

# NEW (clearer intent)
from pirtm import contraction_certificate
cert = contraction_certificate(info)
```

See full migration guide: [`docs/migration/v0.1.1.md`](https://github.com/MultiplicityFoundation/PIRTM/blob/v0.1.1/docs/migration/v0.1.1.md)

## 📝 Known Notes

**4 deprecation warnings** from `pirtm._legacy` import paths remain in this release. These are expected transitional warnings for legacy spectral paths and will be removed in v0.2.0. They do not affect functionality.

## 📦 Installation

```bash
pip install pirtm==0.1.1
```

Or upgrade:

```bash
pip install --upgrade pirtm
```


## 🔗 Resources

- **Documentation:** [docs/](https://github.com/MultiplicityFoundation/PIRTM/tree/v0.1.1/docs)
- **API Reference:** [docs/api/](https://github.com/MultiplicityFoundation/PIRTM/tree/v0.1.1/docs/api)
- **Examples:** [examples/](https://github.com/MultiplicityFoundation/PIRTM/tree/v0.1.1/examples)
- **Conformance Tests:** [tests/conformance/](https://github.com/MultiplicityFoundation/PIRTM/tree/v0.1.1/tests/conformance)
- **PIRTM Language Spec:** [docs/PIRTM_LANGUAGE_SPEC.md](https://github.com/MultiplicityFoundation/PIRTM/blob/v0.1.1/docs/PIRTM_LANGUAGE_SPEC.md)


## 🙏 Acknowledgments

This release reflects focused effort on production-readiness, spec alignment, and developer experience. Thank you to all contributors and reviewers.

---

**Full Changelog:** [v0.1.0...v0.1.1](https://github.com/MultiplicityFoundation/PIRTM/compare/v0.1.0...v0.1.1)

```

***

## Release Commands

### Step 1: Tag Release
```bash
cd PIRTM
git tag -a v0.1.1 -m "PIRTM v0.1.1 - API Clarity & Conformance Hardening"
git push origin v0.1.1
```


### Step 2: Build Artifacts

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build
make build

# Optional: Generate SBOM (if syft installed)
make sbom

# Optional: Sign (if cosign configured)
make sign

# Verify integrity
make verify
```


### Step 3: Upload to PyPI

```bash
# Test PyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Verify test installation
pip install --index-url https://test.pypi.org/simple/ pirtm==0.1.1

# If test passes, upload to production PyPI
python -m twine upload dist/*
```


### Step 4: GitHub Release

1. Navigate to https://github.com/MultiplicityFoundation/PIRTM/releases/new
2. Select tag: `v0.1.1`
3. Title: `PIRTM v0.1.1 — API Clarity & Conformance Hardening`
4. Paste release description (above)
5. Attach artifacts: `dist/*.whl`, `dist/*.tar.gz`, SBOM (if generated)
6. ✅ Publish release

### Step 5: Announcement

Update Phase-Mirror CHANGELOG:

```markdown
## Phase-Mirror CHANGELOG

### 2026-03-02: PIRTM v0.1.1 Released

PIRTM Guardian has been updated to v0.1.1 with:
- Clearer certificate API (`contraction_certificate()` primary, `ace_certificate()` for diagnostics)
- PETC coverage validation CLI tools
- Full conformance test suite (17/17 passing)
- Enhanced documentation and examples

Phase-Mirror governance validators should update PIRTM dependency:
```toml
[dependencies]
pirtm = "^0.1.1"
```

Migration guide: https://github.com/MultiplicityFoundation/PIRTM/blob/v0.1.1/docs/migration/v0.1.1.md

```

***

## Post-Release Verification

### Checklist (within 1 hour of release)

- ⏳ Verify PyPI listing: https://pypi.org/project/pirtm/0.1.1/
- ⏳ Test fresh install: `pip install pirtm==0.1.1`
- ⏳ Run quickstart from README
- ⏳ Verify GitHub Release appears: https://github.com/MultiplicityFoundation/PIRTM/releases
- ⏳ Check that docs render correctly on GitHub
- ⏳ Monitor for install errors (PyPI downloads page)

### Smoke Test Script

```python
# test_v0_1_1_smoke.py
"""Smoke test for PIRTM v0.1.1 release"""
import numpy as np
from pirtm import step, contraction_certificate, ace_certificate

def test_quickstart():
    """Verify README quickstart works"""
    x = np.ones(4)
    xi = 0.3 * np.eye(4)
    lam = 0.2 * np.eye(4)
    T = lambda v: 0.8 * v
    G = np.zeros(4)
    P = lambda v: v
    
    x_next, info = step(x, xi, lam, T, G, P, epsilon=0.05, op_norm_T=0.8)
    
    # Primary API
    cert = contraction_certificate(info)
    assert cert.certified
    print(f"✓ contraction_certificate: certified={cert.certified}")
    
    # Advanced API
    ace = ace_certificate(info)
    assert ace.certified
    print(f"✓ ace_certificate: q_max={ace.q_max:.4f}, margin={ace.margin:.4f}")

if __name__ == '__main__':
    test_quickstart()
    print("\n✅ PIRTM v0.1.1 smoke test PASSED")
```

Run after install:

```bash
pip install pirtm==0.1.1
python test_v0_1_1_smoke.py
```


***

## Next Steps (Post-Release)

### Week 3-4: MTPI Integration

With PIRTM v0.1.1 stable, proceed to MTPI development:

```rust
// MTPI can now depend on stable PIRTM v0.1.1
[dependencies]
pyo3 = "0.20"

// Cargo.toml for mtpi-core
[dependencies.pirtm]
# Reference stable PyPI release
```

**Integration path:**

1. MTPI `pirtm_bridge.rs` uses `contraction_certificate()`
2. MTPI validation tests pass with PIRTM v0.1.1
3. MTPI v0.1.0 ships with clean PIRTM dependency

### Week 5+: PIRTM v0.2.0 Planning

**Roadmap items:**

- Remove `pirtm._legacy` deprecations (breaking change)
- Formal verification track (Coq proofs for ML0-001)
- Enhanced PETC coverage analytics
- Zero-knowledge certificate proofs (zk-SNARK integration)

***

## Release Decision: AFFIRMED ✅

**All gates green. v0.1.1 is GO for release.**

**Release Engineer:** Ready to execute release sequence
**Quality Gate:** PASS (17/17 conformance, 207/207 tests)
**Documentation:** COMPLETE
**Breaking Changes:** NONE
**Risk Level:** LOW

**Proceed with release commands above.**

🚀 **PIRTM v0.1.1 release approved and ready to ship.**

