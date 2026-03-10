# PIRTM Liberation Project Tracker Setup Guide

**Purpose**: Define the GitHub project board structure, milestones, and automation for the 4-phase PIRTM Liberation roadmap (March 8 – July 12, 2026).

**Document Status**: Ready for implementation  
**Target Repositories**: 
- [`MultiplicityFoundation/PIRTM`](https://github.com/MultiplicityFoundation/PIRTM) (primary)
- [`MultiplicityFoundation/Tooling`](https://github.com/MultiplicityFoundation/Tooling) (integration reference)

---

## GitHub Project Board Structure

### Board Configuration

**Name**: `PIRTM Liberation (130-day roadmap)`  
**Type**: Table (new GitHub Projects)  
**Visibility**: Public (allows community tracking)

### Columns & Automation

| Column | Automation | Purpose |
|--------|-----------|---------|
| **📋 Backlog** | Auto-add issues via label `pirtm-liberation` | Entry point for all work |
| **🔖 Ready** | Move when all acceptance criteria known | Ready to start this sprint |
| **🏗️ In Progress** | Manual move when work begins | Currently being worked on |
| **👀 Review** | Automatic on PR open; move manually on code review | Awaiting review/feedback |
| **✅ Done** | Automatic on issue close + PR merge | Released or deployed |

### Filtering & Views

**Pre-built views** (visible from board tabs):

1. **By Phase**: Filter by phase label (phase-1, phase-2, phase-3, phase-4)
2. **By Owner**: Filter by assignee
3. **By Week**: Group by milestone (ends on Friday of each week)
4. **Blockers**: Show only issues with "blocked" label

---

## GitHub Milestones

Each phase gets **one sprint milestone + one delivery milestone**:

### Phase 1: Backend Abstraction (Days 0–7)

| Milestone | Date | Target | Issues |
|-----------|------|--------|--------|
| `Phase 1 Sprint` | 2026-03-08 → 2026-03-15 | 6 tasks, 0 blockers | 6–8 issues |
| `Phase 1 Complete` | 2026-03-15 | Ship backend protocol + tests | 1 epic issue |

### Phase 2: MLIR Emission (Days 8–37)

| Milestone | Date | Target | Issues |
|-----------|------|--------|--------|
| `Phase 2 Sprint (Week 1)` | 2026-03-16 → 2026-03-22 | ADR-007 + MLIR lowering start | 8–10 |
| `Phase 2 Sprint (Week 2)` | 2026-03-23 → 2026-03-29 | MLIREmitter core logic | 8–10 |
| `Phase 2 Sprint (Week 3)` | 2026-03-30 → 2026-04-05 | Transpiler CLI integration | 8–10 |
| `Phase 2 Sprint (Week 4)` | 2026-04-06 → 2026-04-12 | Verification tests + polish | 8–10 |
| `Phase 2 Complete` | 2026-04-14 | Ship `pirtm transpile --output mlir` | 1 epic |

### Phase 3: Type System Enforcement (Days 38–97)

| Milestone | Date | Target | Issues |
|-----------|------|--------|--------|
| `Phase 3 Sprint (Week 1–2)` | 2026-04-15 → 2026-04-28 | ADR-008 + MLIR dialect def | 10–12 |
| `Phase 3 Sprint (Week 3–4)` | 2026-04-29 → 2026-05-12 | Type inference engine | 10–12 |
| `Phase 3 Sprint (Week 5–6)` | 2026-05-13 → 2026-05-26 | Verification pass (C++) | 10–12 |
| `Phase 3 Sprint (Week 7–8)` | 2026-05-27 → 2026-06-09 | Type tests + integration | 10–12 |
| `Phase 3 Complete` | 2026-06-12 | Ship compile-time contractivity checking | 1 epic |

### Phase 4: Standalone Runtime (Days 98–127)

| Milestone | Date | Target | Issues |
|-----------|------|--------|--------|
| `Phase 4 Sprint (Week 1)` | 2026-06-13 → 2026-06-19 | ADR-009 + LLVM codegen | 10–12 |
| `Phase 4 Sprint (Week 2)` | 2026-06-20 → 2026-06-26 | Runtime library + bindings | 10–12 |
| `Phase 4 Sprint (Week 3)` | 2026-06-27 → 2026-07-03 | Multi-backend executor harness | 10–12 |
| `Phase 4 Sprint (Week 4)` | 2026-07-04 → 2026-07-10 | Wheel packaging + CI/CD | 8–10 |
| `Phase 4 Complete` | 2026-07-12 | Ship standalone runtime (LLVM + wheels) | 1 epic |

---

## GitHub Labels

### Phase Labels

- `phase-1`: Backend Abstraction (core modules)
- `phase-2`: MLIR Emission & Transpiler
- `phase-3`: Type System & Verification
- `phase-4`: Standalone Runtime & Wheels

### Priority Labels

- `priority/blocker`: Blocks another task or phase
- `priority/high`: Must complete in this sprint
- `priority/medium`: Should complete in this sprint
- `priority/low`: Nice to have; can slip to next sprint

### Type Labels

- `type/adr`: Architecture Decision Record
- `type/code`: Implementation (Python/C++/MLIR)
- `type/test`: Tests (unit, integration, regression)
- `type/docs`: Documentation or examples
- `type/chore`: Infrastructure, CI/CD, tooling

### Status Labels

- `status/blocked`: Waiting on external dependency or other issue
- `status/ready`: All acceptance criteria known; ready to start
- `status/in-review`: PR open; awaiting feedback
- `status/merged`: PR merged; in release branch

### Component Labels

- `component/backend`: Backend abstraction (Phase 1)
- `component/mlir`: MLIR lowering, dialect, IR (Phase 2–3)
- `component/type-system`: Type inference, contractivity (Phase 3)
- `component/llvm`: LLVM codegen, runtime library (Phase 4)
- `component/cli`: CLI and configuration
- `component/testing`: Test infrastructure, coverage

---

## Issue Templates

### Phase Completion Checklist (Epic)

```markdown
# Phase X Complete: [Title]

**Phase Owner**: @username  
**Target Date**: 2026-XX-XX  
**Release**: vX.Y.Z

## Acceptance Criteria

- [ ] All sub-issues closed
- [ ] All PR reviews completed
- [ ] Test coverage >= 90%
- [ ] Documentation updated
- [ ] Exit gates passed (see below)

## Exit Gates

- [ ] [Gate 1: specific metric]
- [ ] [Gate 2: specific metric]
- [ ] [Gate 3: specific metric]

## Sub-issues

- #[issue]: Task description
- #[issue]: Task description

## Related PRs

- #[pr]: PR title
- #[pr]: PR title

## Notes

[Release notes, caveats, follow-ups]
```

### Task Issue

```markdown
# [Task Title]

**Phase**: Phase X  
**Owner**: @username  
**Estimate**: 2–3 days  
**Dependencies**: #[blocking-issue] (if any)

## Description

[What needs to be done and why]

## Acceptance Criteria

- [ ] Criterion 1 met
- [ ] Criterion 2 met
- [ ] Tests pass with `pytest src/pirtm/tests/...`
- [ ] Code review approved

## Definition of Done

- [x] Issue scoped clearly
- [ ] Owner assigned
- [ ] Story points estimated
- [ ] Ready to start (all blockers resolved)

## Notes

[Technical details, design links, references]
```

---

## Initial Phase 1 Issues

Below is the raw GitHub issue data (GitHub CLI format) for Phase 1. Copy/paste into GitHub or use the `gh issue create` command.

### Issue 1: ADR-006 Review & Approval [Epic]

```yaml
title: "ADR-006: Backend Abstraction — Review & Approval"
labels: [phase-1, type/adr, priority/blocker]
milestone: "Phase 1 Complete"
body: |
  **Linked Issue**: Part of Phase 1 (Backend Abstraction)
  
  ## Objective
  Review, discuss, and approve ADR-006 (backend abstraction protocol).
  
  ## Acceptance Criteria
  - [x] ADR-006 drafted (see /pirtm/docs/adr/ADR-006-backend-abstraction.md)
  - [ ] Core team review comments addressed
  - [ ] Team signs off on protocol design
  - [ ] Decision recorded as "Approved" in ADR
  
  ## Related PRs
  - (none yet; submit ADR for review)
  
  ## Notes
  - ADR-006 references ADR-004 (normative spec)
  - Protocol uses typing.Protocol (Python 3.8+)
  - Unblocks all backend implementation work
```

### Issue 2: Create Backend Module Structure

```yaml
title: "Phase 1.1: Create /backend module with protocol & registry"
labels: [phase-1, type/code, component/backend, priority/high]
milestone: "Phase 1 Sprint"
assignee: "core-team-lead"
body: |
  **Phase**: Phase 1 (Backend Abstraction)
  **Owner**: [assign]
  **Days 1–2 of sprint**
  
  ## Task
  Create the core backend infrastructure:
  - `src/pirtm/backend/__init__.py` (220 lines)
    - TensorBackend protocol definition
    - BackendRegistry class
    - get_backend(), set_default_backend() functions
  - Organize imports for clean API surface
  
  ## Acceptance Criteria
  - [ ] Module structure created under `src/pirtm/backend/`
  - [ ] Protocol has all 25+ required operations
  - [ ] Registry implements register(), get(), set_default(), list_available()
  - [ ] Type hints are correct (Protocol, Array, Scalar types)
  - [ ] __all__ exports are clear
  - [ ] Zero failing tests (existing tests should still pass)
  
  ## Code Links
  - Protocol spec: ../docs/adr/ADR-006-backend-abstraction.md
  
  ## Notes
  - Use typing.Protocol (not ABC); allows external implementations
  - Document each method with docstring + type hints
  - Plan: NumPy backend comes next (Issue 3)
```

### Issue 3: Implement NumPy Backend Wrapper

```yaml
title: "Phase 1.2: NumPy backend reference implementation"
labels: [phase-1, type/code, component/backend, priority/high]
milestone: "Phase 1 Sprint"
assignee: "core-team-lead"
body: |
  **Phase**: Phase 1 (Backend Abstraction)
  **Depends on**: #2 (backend module structure)
  **Days 2–3 of sprint**
  
  ## Task
  Implement NumpyBackend class as reference implementation.
  - `src/pirtm/backend/numpy_backend.py` (150 lines)
  - Wraps all NumPy operations into protocol methods
  - Auto-register with BackendRegistry
  
  ## Acceptance Criteria
  - [ ] NumpyBackend implements all protocol methods
  - [ ] get_backend("numpy") returns working instance
  - [ ] All 25+ operations delegate correctly to NumPy
  - [ ] Scalar operations return floats (not 0-d arrays)
  - [ ] Existing tests still pass
  - [ ] Unit tests for backend (test_numpy_backend.py): >90% coverage
  
  ## Example Test
  ```python
  backend = get_backend("numpy")
  assert backend.name() == "numpy"
  A = backend.eye(3)
  x = backend.ones((3,))
  result = backend.matmul(A, x)
  assert backend.norm(result) > 0
  ```
  
  ## Notes
  - Scalar operations (norm, dot, mean) should return Python float
  - Array operations return numpy arrays
  - Copy docstrings from TensorBackend protocol
```

### Issue 4: Refactor Core Modules (recurrence.py, projection.py)

```yaml
title: "Phase 1.3: Refactor recurrence.py & projection.py for backend abstraction"
labels: [phase-1, type/code, component/backend, priority/high]
milestone: "Phase 1 Sprint"
assignee: "core-team-lead"
body: |
  **Phase**: Phase 1 (Backend Abstraction)
  **Depends on**: #3 (NumPy backend works)
  **Days 3–4 of sprint**
  
  ## Task
  Remove direct NumPy coupling from core computation modules.
  
  **Files to refactor**:
  1. `src/pirtm/recurrence.py`
     - Remove `import numpy`
     - Add `backend: TensorBackend = None` parameter to public functions
     - Replace all `np.*` calls with `backend.*()`
     - Default to `get_backend()` if not provided
  
  2. `src/pirtm/projection.py`
     - Same pattern as recurrence.py
  
  ## Acceptance Criteria
  - [ ] Zero direct `import numpy` in recurrence.py
  - [ ] Zero direct `import numpy` in projection.py
  - [ ] All public functions accept optional backend parameter
  - [ ] Existing tests still pass (no behavioral changes)
  - [ ] New parameterized tests added (test with mock backend)
  - [ ] Code review approved
  
  ## Refactoring Pattern
  ```python
  # BEFORE
  import numpy as np
  result = np.matmul(A, x)
  
  # AFTER
  from .backend import get_backend
  backend = get_backend() if backend is None else backend
  result = backend.matmul(A, x)
  ```
  
  ## Notes
  - Do NOT change API (parameters, return types)
  - All tests must pass without modification
  - Update docstrings to document backend parameter
```

### Issue 5: Refactor Core Modules (gain.py, certify.py)

```yaml
title: "Phase 1.4: Refactor gain.py & certify.py for backend abstraction"
labels: [phase-1, type/code, component/backend, priority/high]
milestone: "Phase 1 Sprint"
assignee: "core-team-member-2"
body: |
  **Phase**: Phase 1 (Backend Abstraction)
  **Depends on**: #4 (basic refactoring pattern established)
  **Days 4–5 of sprint**
  
  ## Task
  Refactor remaining core modules (same pattern as #4).
  
  **Files to refactor**:
  1. `src/pirtm/gain.py`
  2. `src/pirtm/certify.py`
  
  ## Acceptance Criteria
  - [ ] Zero direct `import numpy` in gain.py
  - [ ] Zero direct `import numpy` in certify.py
  - [ ] All public functions accept optional backend parameter
  - [ ] Existing tests pass
  - [ ] Parameterized backend tests added
  - [ ] Code review approved
  
  ## Notes
  - Follow refactoring pattern from #4
  - Parallel work with #4 is fine (different modules)
  - After this issue, all core modules are decoupled
```

### Issue 6: Write Parameterized Backend Tests

```yaml
title: "Phase 1.5: Create parameterized backend test suite"
labels: [phase-1, type/test, component/backend, priority/high]
milestone: "Phase 1 Sprint"
assignee: "qa-lead"
body: |
  **Phase**: Phase 1 (Backend Abstraction)
  **Depends on**: #5 (all core modules refactored)
  **Days 5–6 of sprint**
  
  ## Task
  Create comprehensive test suite for backend abstraction.
  
  **Files to create**:
  1. `src/pirtm/tests/test_backend_protocol.py` (140 lines)
     - Test protocol compliance for NumPy backend
     - Parameterized with @pytest.mark.parametrize("backend", ["numpy"])
     - Test all 25+ operations with edge cases
  
  2. `src/pirtm/tests/test_recurrence_multibackend.py` (200 lines)
     - Integration tests: recurrence loop with backend abstraction
     - Verify same results from NumPy backend
     - Test with mock backend to verify calls
  
  3. `src/pirtm/tests/test_backend_registry.py` (80 lines)
     - Test BackendRegistry.register(), get(), set_default()
     - Test list_available()
     - Test error handling (unknown backend names)
  
  ## Acceptance Criteria
  - [ ] Protocol compliance tests: >90% backend method coverage
  - [ ] Recurrence loop integrated tests pass
  - [ ] Registry tests all pass
  - [ ] Test suite runs in < 5 seconds
  - [ ] All tests pass with pytest
  
  ## Command to Run
  ```bash
  pytest src/pirtm/tests/test_backend_*.py -v --cov=src/pirtm/backend
  ```
  
  ## Notes
  - Use pytest fixtures for backend setup
  - Mock backends can be simple (return zeros, ones, etc.)
  - Plan for easy addition of new backends in Phase 2+
```

### Issue 7: Phase 1 Exit Gate & Merge

```yaml
title: "Phase 1 Complete: Backend Abstraction shipped"
labels: [phase-1, type/adr, priority/blocker]
milestone: "Phase 1 Complete"
body: |
  **Phase**: Phase 1 (Backend Abstraction)
  **Target Date**: 2026-03-15
  **Status**: Opens after all Phase 1 tasks complete
  
  ## Exit Criteria
  - [x] ADR-006 approved
  - [x] Backend protocol + registry implemented (Issue 2)
  - [x] NumPy backend wrapper complete (Issue 3)
  - [x] recurrence.py & projection.py refactored (Issue 4)
  - [x] gain.py & certify.py refactored (Issue 5)
  - [x] Parameterized test suite complete (Issue 6)
  - [ ] All tests passing: `pytest src/pirtm/tests/ -q`
  - [ ] Code coverage >= 90% for backend module
  - [ ] PR merged to main branch
  - [ ] Tag: `phase-1/complete` added
  
  ## PR Checklist
  - [ ] All commits are atomic and well-commented
  - [ ] 2+ code reviews completed
  - [ ] CHANGELOG.md updated
  - [ ] PIRTM_LIBERATION_ROADMAP.md updated (Phase 1 status)
  - [ ] Running notes document created: /docs/PHASE_1_COMPLETION_REPORT.md
  
  ## Release Notes
  ```
  # PIRTM v0.2.0: Backend Abstraction
  
  **Major Change**: Core PIRTM modules are now backend-agnostic.
  
  - Introduced TensorBackend protocol (25+ operations)
  - BackendRegistry for pluggable backends
  - NumPy remains default; GPU/MLIR/LLVM slots in cleanly
  - Zero API changes; fully backward compatible
  
  **Migration Guide**: See /docs/PHASE_1_MIGRATION.md
  ```
  
  ## What Unblocks
  - Phase 2 can begin immediately: MLIR lowering
  - Community can implement custom backends (GPU, JAX, etc.)
```

---

## GitHub Actions Automation

### Workflow: Auto-label PRs by Phase

```yaml
# .github/workflows/phase-labeling.yml
name: Phase Auto-Labeling

on: [pull_request]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeling@v1
        with:
          files: |
            src/pirtm/backend/** -> phase-1
            src/pirtm/mlir/** -> phase-2,phase-3
            src/pirtm/runtime/** -> phase-4
          add-labels: component/[component-from-path]
```

### Workflow: Sprint Progress Reporting

```yaml
# .github/workflows/sprint-report.yml
name: Weekly Sprint Report

on:
  schedule:
    - cron: "0 17 * * 5"  # Every Friday 5 PM UTC

jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - name: Generate sprint progress
        run: |
          # Count issues by status in current milestone
          gh issue list \
            --milestone "Phase $PHASE Sprint" \
            --label "status/done" \
            --json number | wc -l
          
          # Post summary to project board or releases
```

---

## Setting Up This Project Board

### Step 1: Create Project (GitHub Web UI)

1. Go to [MultiplicityFoundation/PIRTM](https://github.com/MultiplicityFoundation/PIRTM) → **Projects** tab
2. Click **New project**
3. Choose **Table** template
4. Name: `PIRTM Liberation (130-day roadmap)`
5. Description: `4-phase roadmap for standalone PIRTM runtime (Mar 8 – Jul 12, 2026)`

### Step 2: Configure Board

1. Add columns (in order):
   - 📋 Backlog
   - 🔖 Ready
   - 🏗️ In Progress
   - 👀 Review
   - ✅ Done

2. Set up automation:
   - File → Workflows → auto-add issues with label `pirtm-liberation`
   - File → Workflows → auto-move PRs to Review when opened
   - File → Workflows → auto-move to Done when PR merged

### Step 3: Create Labels

Run these commands:

```bash
gh label create "phase-1" --color "0366d6" --description "Phase 1: Backend Abstraction"
gh label create "phase-2" --color "0366d6" --description "Phase 2: MLIR Emission"
gh label create "phase-3" --color "0366d6" --description "Phase 3: Type System"
gh label create "phase-4" --color "0366d6" --description "Phase 4: Standalone Runtime"

gh label create "priority/blocker" --color "d73a49"
gh label create "priority/high" --color "f97583"
gh label create "priority/medium" --color "ffa500"
gh label create "priority/low" --color "888888"

gh label create "type/adr" --color "66bb6a"
gh label create "type/code" --color "66bb6a"
gh label create "type/test" --color "66bb6a"
gh label create "type/docs" --color "66bb6a"
gh label create "type/chore" --color "66bb6a"

gh label create "status/blocked" --color "d73a49"
gh label create "status/ready" --color "85e89d"
gh label create "status/in-review" --color "f0883e"
gh label create "status/merged" --color "28a745"

gh label create "component/backend" --color "a371f7"
gh label create "component/mlir" --color "a371f7"
gh label create "component/type-system" --color "a371f7"
gh label create "component/llvm" --color "a371f7"
gh label create "component/cli" --color "a371f7"
gh label create "component/testing" --color "a371f7"

gh label create "pirtm-liberation" --color "1f6feb" --description "Part of PIRTM Liberation roadmap"
```

### Step 4: Create Milestones

```bash
# Phase 1
gh milestone create --title "Phase 1 Sprint" \
  --description "Days 0–7: Backend Abstraction" \
  --due-date "2026-03-15"

gh milestone create --title "Phase 1 Complete" \
  --description "Phase 1 delivery: backend protocol shipped" \
  --due-date "2026-03-15"

# Phase 2 (4 weeks)
gh milestone create --title "Phase 2 Sprint (Week 1)" \
  --description "Days 8–14: ADR-007 + MLIR lowering start" \
  --due-date "2026-03-22"

# ... (etc. for all milestones)
```

### Step 5: Bulk-import Initial Issues

Use the issue template above with `gh issue create`:

```bash
gh issue create \
  --title "ADR-006: Backend Abstraction — Review & Approval" \
  --label "phase-1,type/adr,priority/blocker" \
  --milestone "Phase 1 Complete" \
  --body-file issue-adr-006.md

# ... (repeat for Issues 1–7)
```

---

## Monitoring & Reporting

### Weekly Check-in

Every Friday, core team reviews:
1. **Completed issues**: Move to ✅ Done
2. **Blockers**: Any issues with `status/blocked`? Create sub-issues.
3. **Burndown**: Are we on pace? (Issues closed / Issues total)
4. **Risk register**: Any risks materializing?

### Phase Exit Gates

Before moving to next phase:
- [ ] All issues in current phase closed
- [ ] All tests passing (100%)
- [ ] Code coverage >= 90%
- [ ] ADR approved and documented
- [ ] Release notes drafted
- [ ] Team sign-off on completion

### Success Metrics (KPIs)

| KPI | Phase 1 Target | Phase 2–4 Target |
|-----|---|---|
| Sprint velocity (issues/week) | 4–6 | 8–10 |
| Test coverage (%) | ≥90 | ≥95 |
| On-time completion | Yes | Yes |
| Critical blockers | 0 | 0 |
| Code review turnaround (hours) | <24 | <24 |

---

## Quick Links

- **Roadmap document**: [PIRTM_LIBERATION_ROADMAP.md](./PIRTM_LIBERATION_ROADMAP.md)
- **ADR-006**: [ADR-006-backend-abstraction.md](./adr/ADR-006-backend-abstraction.md)
- **GitHub Projects**: [MultiplicityFoundation/PIRTM/projects](https://github.com/MultiplicityFoundation/PIRTM/projects)
- **GitHub Discussions**: [PIRTM Liberation Planning](https://github.com/MultiplicityFoundation/PIRTM/discussions)

