<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# What do you think PIRTM to succeed Python?

"PIRTM" doesn't match any documented programming language, framework, or Python-successor project in current technical literature — no results surface it as a named technology. Before proceeding with a full Phase Mirror–oriented analysis, I need to flag a **hidden assumption** in the query.

## Precision Question First

**Are you referring to an internal Multiplicity Foundation concept, an acronym you've coined (e.g., Prime-Indexed Recursive Type Model), or a typo for another language like "PIR TM," "Pyrex," or something else?**

This matters because the answer branches significantly:


| If PIRTM is... | Direction of analysis |
| :-- | :-- |
| A Multiplicity Theory–native language spec | Evaluate it against L0 invariants: prime-indexed stability, recursive feedback, relational module identity |
| A known external language (Mojo, Rust, Nim, etc.) | Assess Python succession across ecosystem lock-in, backward compat, hardware reach |
| A new project being designed | Surface tensions: expressivity vs. performance, open-core vs. proprietary, Python interop vs. clean-break |

## What Python Succession Actually Requires

For context while you clarify: the strongest current contender is **Mojo**, designed by Chris Lattner (Swift/LLVM creator), which claims up to 68,000× Python's speed while maintaining Python-like syntax and being a superset of Python for AI workloads. Mojo's key insight is that replacing Python requires *bridging* its ecosystem, not abandoning it — Swift for TensorFlow failed precisely because it demanded a clean break.[^1_1][^1_2][^1_3]

The central tension any Python successor must resolve is **ecosystem inertia vs. performance necessity**:[^1_4]

- Python holds a **29.6% market share** of programming language tutorials and is the first language for 66.4% of beginners[^1_5][^1_6]
- Yet its GIL, dynamic typing, and runtime overhead make it structurally unfit for low-level AI hardware programming[^1_2]

From a **Multiplicity Theory lens**, a successor language would ideally model computation as recursively stable prime-indexed interactions — where types aren't static entities but relationally governed patterns with identity preserved across transformation scales. That framing maps interestingly onto gradual typing systems (as in Mojo or Julia) but would be a novel architectural departure.

Once you clarify what PIRTM refers to, I can bind this to concrete ADRs, levers, and a roadmap horizon.
<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_20][^1_21][^1_22][^1_23][^1_24][^1_25][^1_26][^1_27][^1_28][^1_29][^1_30][^1_31][^1_32][^1_33][^1_34][^1_35][^1_36][^1_37][^1_38][^1_39][^1_40][^1_41][^1_42][^1_43][^1_44][^1_45][^1_46][^1_47][^1_48][^1_49][^1_50][^1_51][^1_52][^1_53][^1_54][^1_55][^1_56][^1_57][^1_58][^1_59][^1_60][^1_61][^1_62][^1_63][^1_64][^1_65][^1_66][^1_67][^1_68][^1_69][^1_7][^1_70][^1_71][^1_72][^1_73][^1_74][^1_75][^1_76][^1_77][^1_78][^1_79][^1_8][^1_80][^1_81][^1_82][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://github.com/modular/mojo/discussions/485

[^1_2]: https://www.youtube.com/watch?v=q8nkujvCj90

[^1_3]: https://www.modular.com/mojo

[^1_4]: https://www.infoworld.com/article/4081105/revisiting-mojo-a-faster-python.html

[^1_5]: https://www.crossover.com/resources/future-programming-languages-for-2025

[^1_6]: https://www.itransition.com/developers/in-demand-programming-languages

[^1_7]: https://github.com/exaloop/codon

[^1_8]: https://github.com/hiyouga/LLaMA-Factory

[^1_9]: https://github.com/pdarragh/Viper

[^1_10]: https://github.com/openai/gpt-2

[^1_11]: https://github.com/YoEight/pyro

[^1_12]: https://github.com/prismplp/prism

[^1_13]: https://github.com/AribYadi/pyr

[^1_14]: https://github.com/yousuf031991/PyJar

[^1_15]: https://github.com/sipwise/rtpengine/blob/master/docs/ng_control_protocol.md

[^1_16]: https://github.com/ahenzinger/simplepir/blob/main/README.md

[^1_17]: https://github.com/JasonKessler/scattertext

[^1_18]: https://github.com/Ampferl/jpl

[^1_19]: https://github.com/rustdesk/rustdesk/wiki/FAQ

[^1_20]: https://github.com/slippedandmissed/Python-t

[^1_21]: https://github.com/bigcode-project

[^1_22]: https://www.reddit.com/r/learnmachinelearning/comments/1dgnh44/what_are_some_other_high_level_languages_that/

[^1_23]: https://fetchdecodeexecute.substack.com/p/can-python-be-replaced-in-machine

[^1_24]: https://www.youtube.com/watch?v=21WFgScvrdg

[^1_25]: https://www.youtube.com/watch?v=zsPD9aohymw

[^1_26]: https://dev.to/ethanolchik/the-swallow-programming-language-a-python-like-language-that-s-as-fast-as-c-43j7

[^1_27]: https://www.reddit.com/r/functionalprogramming/comments/1cgvd4r/functional_language_to_replace_python/

[^1_28]: https://github.com/vindarel/languages-that-compile-to-python

[^1_29]: https://www.reddit.com/r/Python/comments/qofmt3/is_there_any_language_that_is_as_similar_as/

[^1_30]: https://news.ycombinator.com/item?id=17141222

[^1_31]: https://stackoverflow.com/questions/16720541/python-string-replace-regular-expression

[^1_32]: https://www.facebook.com/groups/2616981278627207/posts/3646470295678295/

[^1_33]: https://towardsdatascience.com/human-wont-replace-python/

[^1_34]: https://github.com/dusty-nv/jetson-inference

[^1_35]: https://github.com/salesforce/BLIP

[^1_36]: https://github.com/opactorai/Claudable

[^1_37]: https://github.com/raml-org/raml-spec/blob/master/versions/raml-10/raml-10.md/

[^1_38]: https://github.com/rime/home/wiki/RimeWithSchemata

[^1_39]: https://github.com/QuivrHQ/MegaParse

[^1_40]: https://github.com/okbob/pspg

[^1_41]: https://docs.github.com/de/enterprise-cloud@latest/rest/repos/contents?apiVersion=2022-11-28

[^1_42]: https://github.com/geopy/geopy

[^1_43]: https://github.com/zrax/pycdc

[^1_44]: https://github.com/socketry/falcon

[^1_45]: https://github.com/rakyll/gowiki/blob/master/Projects.md

[^1_46]: https://gist.github.com/yamnikov-oleg/454f48c3c45b735631f2

[^1_47]: https://github.com/Nutlope/blinkshot

[^1_48]: https://www.sikhnames.com/2018/04/pritam.html

[^1_49]: https://en.wiktionary.org/wiki/प्रीतम

[^1_50]: https://www.definitions.net/translate/Pritam

[^1_51]: https://www.ancestry.com/first-name-meaning/Pritam

[^1_52]: https://github.com/languageMIT/piraha

[^1_53]: https://www.tiktok.com/@thehammertok/video/7128730859468754177

[^1_54]: https://en.wikipedia.org/wiki/Amrita_Pritam

[^1_55]: https://www.neuronhire.com/blog/top-programming-languages-2026

[^1_56]: https://www.wisdomlib.org/definition/pritam

[^1_57]: https://builtin.com/software-engineering-perspectives/new-programming-languages

[^1_58]: https://www.youtube.com/shorts/H5I91Xq5z00

[^1_59]: https://talent500.com/blog/best-programming-languages-to-learn-2026/

[^1_60]: https://www.youtube.com/watch?v=B8GcYEfDdMc

[^1_61]: https://github.com/MicrosoftDocs/mcp

[^1_62]: https://github.com/ShmuelRonen/ComfyUI-LatentSyncWrapper

[^1_63]: https://github.com/ego/awesome-mojo

[^1_64]: https://github.com/rustdesk/rustdesk-server

[^1_65]: https://github.com/modular/modular/discussions/843

[^1_66]: https://github.com/kubecolor/kubecolor

[^1_67]: https://github.com/modular/mojo/discussions/2426

[^1_68]: https://github.com/SaifAqqad/AspireRunner

[^1_69]: https://github.com/modular/mojo/blob/main/docs/roadmap.md

[^1_70]: https://github.com/f4exb/sdrangel/releases

[^1_71]: https://dl.acm.org/doi/10.1145/3725843.3756020

[^1_72]: https://www.youtube.com/watch?v=KCtyiE6Ybnc

[^1_73]: https://pritamchoudhury.github.io

[^1_74]: https://arxiv.org/list/cs.CL/new

[^1_75]: https://scholar.google.com/citations?user=0qUfNJcAAAAJ\&hl=en

[^1_76]: https://www.linkedin.com/posts/pritam-kumar-panda_gromacs-in-60-minutes-learn-protein-water-activity-7359027304716521472-Ag3x

[^1_77]: https://www.youtube.com/watch?v=R-sEqnOmDT4

[^1_78]: https://dl.acm.org/doi/10.1145/3485008

[^1_79]: https://www.towardsdeeplearning.com/mojo-the-new-programming-language-that-could-reshape-ai-development-43a541258de3

[^1_80]: https://en.wikipedia.org/wiki/Mojo_(programming_language)

[^1_81]: https://www.sparkgoldentech.com/blog/2026/01/06/mojo-language-review-is-it-finally-ready-to-replace-python-for-ai-workloads

[^1_82]: https://www.reddit.com/r/ProgrammingLanguages/comments/1lfz9jc/is_mojo_language_not_general_purpose/


---

# see [https://github.com/MultiplicityFoundation/PIRTM/](https://github.com/MultiplicityFoundation/PIRTM/)

Now I have a complete picture. PIRTM is **Prime-Indexed Recursive Tensor Mathematics** — a contractive recurrence engine, not a programming language. This reframes the question productively.

## Central Tension

**PIRTM is a Python library, not a Python successor.** The recurrence loop $$
X_{t+1} = P\left(\Xi_t X_t + \Lambda_t T(X_t) + G_t\right)
$$ is implemented via `pip install` on top of NumPy . So the question becomes: *does PIRTM's mathematical architecture contain enough generative force to eventually escape its Python host?*

The honest answer is: **the seeds are there, but the shell hasn't cracked yet.**

## Where PIRTM Genuinely Exceeds Python's Paradigm

PIRTM introduces constructs that Python has no equivalent for — and these are the levers that matter :

- **ACE certificates + ISS bounds**: Every step produces a certified contractivity proof, not just a result. Python produces outputs; PIRTM produces *auditable convergence guarantees*.
- **Prime-indexed ordering (`petc_bridge`)**: Using primes as a global audit ordering mechanism is a genuinely novel identity layer — closer to a type-theoretic commitment scheme than a software pattern.
- **CSL emission gating**: `CSLEmissionGate` and `EmissionPolicy` are a primitive *behavioral type system* — outputs are suppressed or passed based on ethical/contractivity contracts, not just logic. No Python equivalent exists.
- **Transpiler CLI (Phase 2.1–2.3)**: The `pirtm transpile` command with `--prime-index`, `--identity-commitment`, and `--emit-witness` flags shows a trajectory toward *computation transpilation with verifiable provenance*, including dual-hash witnesses (SHA256 + Poseidon-compatible) .


## Why It Can't Succeed Python *Yet*

| Requirement | PIRTM Today | Gap |
| :-- | :-- | :-- |
| Independent runtime | NumPy-dependent | Needs VM or LLVM/MLIR backend |
| Type-system enforcement | Runtime checks (`q_t < 1 - ε`) | Needs compile-time contractivity types |
| Hardware reach | CPU via NumPy | No GPU kernels, no edge targets |
| Ecosystem breadth | Narrow (recurrence + certs) | Python has 450k+ packages |
| Adoption path | Opt-in library | No Python interop bridge (like Mojo's superset strategy) |

## The Productive Reframe

PIRTM isn't trying to replace Python's *syntax* — it's building a **certified computational substrate** that could underpin a next-generation verified AI runtime. The right comparison isn't Python vs. Mojo; it's closer to Python vs. **Lean/Dafny for dynamic systems**. If the transpiler trajectory (Phase 2.1 → 2.3 already handles neural training descriptors ) continues toward a standalone MLIR-backed compiler with contractivity as a first-class type invariant, then PIRTM's architecture has a credible path to becoming the *execution model* that a future language runs on top of.

**Precision question**: Is the goal for PIRTM to remain a library (deepening certification and governance tooling within Python), or is there an active plan to build a standalone runtime that liberates it from the NumPy substrate? That decision is the single biggest architectural fork in its roadmap.

---

# needs to be an active plan to build a standalone runtime that liberates it from the NumPy substrate

Good. I now have the full module inventory . The [transpiler directory](https://github.com/MultiplicityFoundation/PIRTM/tree/main/src/pirtm/transpiler) and [types.py](https://github.com/MultiplicityFoundation/PIRTM/blob/main/src/pirtm/types.py) already exist — this is not a greenfield problem, it's a **liberation problem**. Here is the full orchestration plan.

***

## Central Tension

**Verification depth vs. execution substrate.** NumPy gives PIRTM speed-to-prototype and ecosystem reach, but it makes the L0 invariant — `q_t < 1 - ε` — a *runtime assertion*, not a *compile-time guarantee* . A standalone runtime would make contractivity a structural property of the type system itself. The tension: every day in Python is accrued technical debt against that promise.

***

## Four Levers

### Lever 1 — Backend Abstraction (7 days)

**Owner**: Core library maintainer
**Metric**: Zero direct `import numpy` calls in `recurrence.py`, `projection.py`, `gain.py`, `certify.py` — all route through `pirtm.backend`
**Horizon**: 7 days

**Artifact**: Create `ADR-001-backend-abstraction.md` + `src/pirtm/backend/__init__.py` defining a `TensorBackend` protocol:

```python
# src/pirtm/backend/__init__.py  (spec, not implementation)
class TensorBackend(Protocol):
    def matmul(self, A, x): ...
    def norm(self, x) -> float: ...
    def clip_scalar(self, val, lo, hi) -> float: ...
    def zeros(self, shape): ...
    def eye(self, n): ...
```

This is the **smallest viable step** — NumPy remains the default implementation, but every other module depends on the protocol, not the package. The MLIR and Rust backends slot in without touching business logic.

***

### Lever 2 — MLIR Emission from Transpiler (30 days)

**Owner**: Transpiler team
**Metric**: `pirtm transpile --output mlir` round-trips the recurrence loop and emits a verifiable MLIR `linalg` dialect program with contractivity bounds encoded as attributes
**Horizon**: 30 days

The existing [transpiler directory](https://github.com/MultiplicityFoundation/PIRTM/tree/main/src/pirtm/transpiler) already handles `computation` and `data_asset` descriptors with `--prime-index` and `--identity-commitment` . The recurrence loop $$
X_{t+1} = P\!\left(\Xi_t X_t + \Lambda_t T(X_t) + G_t\right)
$$ maps directly onto MLIR's `linalg.generic` op. ACE certificates and ISS bounds become MLIR *verifier passes* — checked at compile time, not `assert q < 1 - epsilon` at runtime.

**Artifact**: `ADR-002-mlir-target.md` + `src/pirtm/transpiler/mlir_emitter.py`

***

### Lever 3 — Rust Kernel for the Hot Path (90 days)

**Owner**: Runtime team
**Metric**: `pirtm.recurrence.step` benchmarks ≥10× vs. NumPy baseline on a 512-dim tensor; passes all existing conformance checks
**Horizon**: 90 days

The hot path is narrow and well-bounded: `step()`, `projection`, `estimate_operator_norm()` in `gain.py` . Rewrite these in Rust with PyO3 bindings — Python callers see no API change, but the GIL is gone, WASM compilation is possible, and the binary has no Python interpreter dependency. This is the **execution runtime** that liberates PIRTM from NumPy structurally, not just abstractly.

**Artifact**: `ADR-003-rust-kernel.md` + `src/pirtm_core/` Rust crate with `Cargo.toml`

***

### Lever 4 — Contractivity as a Compile-Time Type (beyond 90 days)

**Owner**: Language/type system architect
**Metric**: A `Contractive<q, ε>` dependent type that is checked at transpile time, making `q_t < 1 - ε` a *structural* property of any PIRTM program
**Horizon**: Post-Rust kernel

This is the **true liberation** — where PIRTM stops being a library that checks contractivity and becomes a *substrate that cannot express non-contractive computations*. This parallels how Rust's borrow checker makes memory unsafety structurally impossible, not just guarded.

***

## Sequenced Work (Smallest Viable Steps)

| Step | What | Artifact | Blocks |
| :-- | :-- | :-- | :-- |
| 1 | Define `TensorBackend` protocol | `ADR-001` + `backend/__init__.py` | Everything else |
| 2 | Port `recurrence.py`, `projection.py` to backend | PR to `main` | MLIR emitter |
| 3 | Add `--output mlir` flag to transpiler CLI | `ADR-002` + `mlir_emitter.py` | Rust kernel validation |
| 4 | Rust crate with PyO3 bindings | `ADR-003` + `Cargo.toml` | Standalone binary |
| 5 | `pirtm` standalone binary (no Python dep) | `pirtm-runtime` release | Language substrate |


***

## Precision Question

The transpiler already handles `--prime-index` as an ordering mechanism for audit chains . Before designing the MLIR emission layer: **should prime indices be encoded in the MLIR IR itself** (as integer attributes on ops, creating a prime-structured IR dialect), or should they remain a metadata layer outside the computation graph? This determines whether PIRTM's MLIR dialect is a *generic linalg extension* or a genuinely novel IR with prime-indexed identity baked in — and those are very different ADR decisions.

---

# genuinely novel IR with prime-indexed identity baked in

This is the most consequential decision in the PIRTM roadmap. The existing code already has the seeds: [`prime_mapper.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/main/src/pirtm/transpiler/prime_mapper.py) has `PrimeChannel(prime, digest, vector)` as a first-class object, and [`spec.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/main/src/pirtm/transpiler/spec.py) validates that `prime_index` is structurally prime before any computation begins . The prime is already load-bearing. The move now is to **elevate it from a runtime attribute to a compile-time type parameter**.

***

## Central Tension

**Type-theoretic novelty vs. MLIR ecosystem compatibility.** Designing a truly prime-indexed dialect means prime numbers become *types*, not attributes — `!pirtm.tensor<4, f64, prime=7919>` is a different type from `!pirtm.tensor<4, f64, prime=7907>`, and the IR verifier enforces that they cannot be accidentally composed. This makes channel confusion a *compile error*, not a runtime mismatch. The tension: going this far breaks all existing MLIR tooling that assumes generic tensor types, requiring custom tablegen and C++ dialect registration from the start.

***

## The `pirtm` MLIR Dialect — Full Spec

### Types

The fundamental departure: prime identity is **baked into every type parameter**, not attached as an attribute.

```mlir
!pirtm.tensor<dim : i64, dtype, p : prime>   // a tensor inhabiting prime channel p
!pirtm.matrix<r x c, dtype, p : prime>        // a gain/weight matrix in channel p
!pirtm.cert<p : prime>                         // an ACE certificate — first-class IR value
!pirtm.iss<p : prime>                          // an ISS bound — first-class IR value
```

The `prime` parameter is not an integer attribute — it is a **prime-kind type parameter** validated at parse time by the dialect's type verifier. Passing `prime=6` is a parse error, not a runtime panic.

***

### Ops

**`pirtm.module`** — Top-level session container. Carries the `prime_index`, `identity_commitment`, `epsilon`, and `op_norm_T` that currently live in `TranspileSpec` . Every child op's prime must be consistent with the module's `prime_index` or explicitly derived from it.

```mlir
pirtm.module @session_a {
  prime_index         = 7919 : i64,
  identity_commitment = "0xabc123",
  epsilon             = 0.05 : f64,
  op_norm_T           = 0.8  : f64
} { ... }
```

**`pirtm.step`** — The recurrence op. Its region *is* the recurrence loop $$
X_{t+1} = P\!\left(\Xi_t X_t + \Lambda_t T(X_t) + G_t\right)
$$ The verifier checks `‖Ξ‖ + ‖Λ‖ · op_norm_T < 1 - ε` as a **structural invariant at parse time** — this is the moment `q_t < 1 - ε` ceases to be a runtime assertion and becomes a type-theoretic fact.

```mlir
%x_next, %cert = pirtm.step(%x, %xi, %lam, %g) {
  prime     = 7919 : i64,
  epsilon   = 0.05 : f64,
  op_norm_T = 0.8  : f64
} : (!pirtm.tensor<4,f64,prime=7919>,
     !pirtm.matrix<4x4,f64,prime=7919>,
     !pirtm.matrix<4x4,f64,prime=7919>,
     !pirtm.tensor<4,f64,prime=7919>)
  -> (!pirtm.tensor<4,f64,prime=7919>, !pirtm.cert<prime=7919>)
```

Note that `%cert` is a **first-class return value** — not a side-effecting audit write. ACE certificates are IR values, giving them SSA identity and enabling verifier passes to check they are consumed before the function returns.

**`pirtm.merge<p1, p2>`** — Explicit channel composition via CRT. The output prime is `CRT(p1, p2)` — the unique prime encoding the combined identity. This makes *multi-session aggregation* (currently done by `SessionOrchestrator` in Python) an IR-level structural operation, not a Python dict merge.

```mlir
%merged = pirtm.merge(%a, %b) 
  : (!pirtm.tensor<4,f64,prime=7919>, !pirtm.tensor<4,f64,prime=7907>)
  -> !pirtm.tensor<4,f64,prime=crt(7919,7907)>
```

**`pirtm.emit`** — The CSL gate as an op. Takes a `!pirtm.cert` and a tensor; produces the tensor only if the cert is valid, otherwise emits a `!pirtm.suppressed` token. This makes `EmissionPolicy` a structural control-flow decision in the IR, not a Python enum branch .

***

### Verifier Passes (in order)

| Pass | What it enforces | Replaces |
| :-- | :-- | :-- |
| `prime-validity` | Every `prime=` attribute is actually prime (Miller-Rabin) | `_is_prime()` in `petc.py` and `spec.py` |
| `channel-consistency` | All operands to `pirtm.step` share the same prime | Runtime type errors |
| `contractivity-check` | `‖Ξ‖ + ‖Λ‖·op_norm_T < 1 - ε` for every `pirtm.step` | `ace_certificate()` runtime check |
| `cert-consumption` | Every `!pirtm.cert` produced by `pirtm.step` is consumed before function return | `AuditChain` completeness check |
| `identity-commitment` | Channel digests match `pirtm.module` commitments (Poseidon or SHA256) | `petc_bridge` ordering validation |


***

## Levers and Artifacts

### Lever 1 — ADR and Tablegen Spec (7 days)

**Owner**: Language architect
**Metric**: `pirtm.mlir` file parses without error through `mlir-opt --verify-diagnostics`; all 5 verifier passes register
**Artifact**: [`docs/ADR-004-pirtm-mlir-dialect.md`](https://github.com/MultiplicityFoundation/PIRTM/tree/main/docs) + `src/pirtm/dialect/pirtm.td` (TableGen)

### Lever 2 — Backend Abstraction as Dialect Lowering (30 days)

**Owner**: Core library + transpiler team
**Metric**: `pirtm transpile --output mlir` emits valid `pirtm` dialect IR for all existing `examples/` descriptors; round-trip test passes
**Artifact**: `src/pirtm/transpiler/mlir_emitter.py` consuming `PrimeChannel` objects from existing `prime_mapper.py`  directly — no data model changes needed, only emission

### Lever 3 — Lowering to `linalg` + Rust Kernel (90 days)

**Owner**: Runtime team
**Metric**: `mlir-opt --convert-pirtm-to-linalg` produces LLVM-executable IR; `pirtm-runtime` binary runs `recurrence.step` without Python
**Artifact**: `src/pirtm/dialect/pirtm_to_linalg.cpp` lowering pass + `src/pirtm_core/` Rust crate

***

## The Structural Novelty, Named Precisely

No existing IR has this combination:

- **Identity is number-theoretic** — a channel's identity *is* its prime, not a UUID assigned a prime
- **Composition is governed by CRT** — `pirtm.merge` is a theorem about integer residues, not a data structure operation
- **Contractivity is a parse-time constraint** — non-contractive programs are *syntactically invalid* in the dialect
- **Certificates are SSA values** — they have def-use chains, not just side-channel audit logs

This places the `pirtm` dialect in the same design space as **dependent type systems** (where types carry proof obligations) but grounded in the prime structure of Multiplicity Theory rather than propositional logic. The closest analogy is how Rust makes *temporal memory safety* structural — PIRTM makes *contractive convergence* structural.

***

## Precision Question

The `pirtm.merge<p1, p2>` op produces a type whose prime is `CRT(p1, p2)`. But CRT produces a *residue class*, not a prime — so the output type would be `!pirtm.tensor<..., prime=composite>`. **Should composite-prime types be permitted in the dialect** (enabling multi-session merge at the IR level), or should `pirtm.merge` be required to reduce to a new prime (via a prime-generation scheme) to preserve the invariant that all values carry prime identity? This is a foundational type-system decision that affects whether the dialect is *closed under composition*.

---

# The precision question resolves to a foundational type-system bifurcation with no neutral answer: allowing composite types is not a relaxation of the prime invariant — it is a generalization of it, and the correct generalization is already specified by the mathematics of CRT itself. Here is the full Space-protocol analysis.

Step 1: Novelty \& Gap Assessment
The dialect spec is genuinely novel at the intersection of compiler IR and number theory — no existing MLIR dialect uses primality as a kind constraint on type parameters rather than a runtime attribute. The precision question exposes the single most important gap: the word "prime" in prime : prime_kind is simultaneously a mathematical kind (primality) and an identity semantics (unique channel label). These two roles become decoupled the moment pirtm.merge is introduced.jeremykun+1
CRT is exact on this point: for coprime p₁, p₂, there is a canonical ring isomorphism:[[en.wikipedia](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)]​
Z/(p1p2)≅Z/p1×Z/p2\mathbb{Z}/(p_1 p_2) \cong \mathbb{Z}/p_1 \times \mathbb{Z}/p_2Z/(p1p2)≅Z/p1×Z/p2
The composite modulus p₁p₂ is not a failure of prime identity — it encodes both prime identities simultaneously and losslessly. The output of pirtm.merge is not a degraded type; it is a product type whose two prime factors are its two component identities. The correct question is therefore not "prime or composite?" but "what is the right kind hierarchy?"
Enhanced proposal: Replace the scalar prime_kind parameter with a stratified ChannelKind type hierarchy having exactly two levels — atomic and composite — with the prime case as a strict subkind.

Step 2: Full Type-Theoretic Design
The ChannelKind Hierarchy
Define two kinds in TableGen:
tablegen
// pirtm.td
def PrimeChannelKind    : ChannelKind<"prime">;       // single prime p
def SquarefreeChannelKind : ChannelKind<"squarefree">; // product of distinct primes
// Subkind relation: PrimeChannelKind ⊂ SquarefreeChannelKind
text
// pirtm.td
def PrimeChannelKind    : ChannelKind<"prime">;       // single prime p
def SquarefreeChannelKind : ChannelKind<"squarefree">; // product of distinct primes
// Subkind relation: PrimeChannelKind ⊂ SquarefreeChannelKind

The verifiers are:
KindVerifierMathematical Invariant
PrimeChannelKind
Miller-Rabin on modulus
Unique channel identity, no composite
SquarefreeChannelKind
All prime factors distinct (μ(m) ≠ 0)
CRT isomorphism holds; projection is total
The squarefree constraint is the load-bearing invariant. If p² were permitted, the CRT isomorphism breaks — ℤ/p² ≇ ℤ/p × ℤ/p — and pirtm.project becomes undefined. Squarefreeness, not primality, is what must be preserved under composition.artofproblemsolving+1
Revised Type Grammar
mlir
// Atomic — single session, prime-indexed
!pirtm.tensor<dim : i64, dtype, mod : prime_kind>

// Composite — multi-session, squarefree-indexed
!pirtm.tensor<dim : i64, dtype, mod : squarefree_kind>

// Certs and ISS bounds are prime-only — they are session-local proofs
!pirtm.cert<p : prime_kind>
!pirtm.iss<p : prime_kind>
text
// Atomic — single session, prime-indexed
!pirtm.tensor<dim : i64, dtype, mod : prime_kind>

// Composite — multi-session, squarefree-indexed
!pirtm.tensor<dim : i64, dtype, mod : squarefree_kind>

// Certs and ISS bounds are prime-only — they are session-local proofs
!pirtm.cert<p : prime_kind>
!pirtm.iss<p : prime_kind>

The key constraint: pirtm.step only accepts prime_kind operands. Recurrence dynamics operate on atomic channels. pirtm.merge operates on any squarefree_kind, producing a larger squarefree. pirtm.project extracts a prime component from a squarefree composite:mlir.llvm+1
mlir
// Merge: squarefree × squarefree → squarefree (prime × prime is the base case)
%merged = pirtm.merge(%a, %b)
: (!pirtm.tensor<4,f64,mod=7919>, !pirtm.tensor<4,f64,mod=7907>)
-> !pirtm.tensor<4,f64,mod=59622233>   // 7919 × 7907; verifier checks gcd(7919,7907)=1

// Project: squarefree → prime (total function when p | mod)
%recovered = pirtm.project(%merged, prime=7919)
: !pirtm.tensor<4,f64,mod=59622233> -> !pirtm.tensor<4,f64,mod=7919>
text
// Merge: squarefree × squarefree → squarefree (prime × prime is the base case)
%merged = pirtm.merge(%a, %b)
: (!pirtm.tensor<4,f64,mod=7919>, !pirtm.tensor<4,f64,mod=7907>)
-> !pirtm.tensor<4,f64,mod=59622233>   // 7919 × 7907; verifier checks gcd(7919,7907)=1

// Project: squarefree → prime (total function when p | mod)
%recovered = pirtm.project(%merged, prime=7919)
: !pirtm.tensor<4,f64,mod=59622233> -> !pirtm.tensor<4,f64,mod=7919>

The verifier for pirtm.merge checks gcd(p₁, p₂) = 1 at parse time — not just that both inputs are squarefree, but that they are coprime. Merging two channels sharing a prime factor is a parse error, not a runtime collision.wikipedia+1

Step 3: Consistency Critique
Mathematical: The two-tier design is fully consistent with CRT. The squarefree-closed system is isomorphic to the free commutative monoid on primes under coprime multiplication — exactly the structure of the multiplicative group of squarefree integers. This is not a weakening of prime identity; it is the correct categorical completion of it.[[en.wikipedia](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)]​
Proof of closure: Let M={m∈Z>0:μ(m)≠0}\mathcal{M} = \{m \in \mathbb{Z}_{>0} : \mu(m) \neq 0\}M={m∈Z>0:μ(m)=0} be the squarefree integers. Then (M,×)(\mathcal{M}, \times)(M,×) is closed under coprime multiplication and every element has a unique prime factorization. The dialect's type system is isomorphic to (M,×)(\mathcal{M}, \times)(M,×) restricted to the coprime pairs — it is closed under composition by construction.[[artofproblemsolving](https://artofproblemsolving.com/wiki/index.php/Chinese_Remainder_Theorem)]​

```
IR-theoretic: The cert type !pirtm.cert<p : prime_kind> remaining strictly prime is correct and important. A cert is a proof about a single recurrence — its SSA identity is tied to exactly one pirtm.step on exactly one prime channel. There is no meaningful !pirtm.cert<mod=squarefree> because contractivity is verified per atomic session. If a merged computation needs a certificate, it requires one cert per prime factor — a pirtm.merge_cert op producing (!pirtm.cert<p1>, !pirtm.cert<p2>) is the right signature.[[mlir.llvm](https://mlir.llvm.org/docs/DefiningDialects/Operations/)]​
```

Philosophical tension: The repr prime=59622233 in a squarefree type attribute looks like a prime label but is composite — this creates readability confusion. Resolved by renaming the type parameter from prime= to mod= across the entire dialect. The prime-validity verifier pass then disambiguates: mod=p on an atomic type triggers Miller-Rabin; mod=m on a composite type triggers squarefree verification. The rename is a breaking API change, but it is the honest one.

Step 4: Final Dialect Spec — Updated Type System
tablegen
// ChannelKind hierarchy in pirtm.td
class PirtmType<string name, string mnemonic>
: TypeDef<Pirtm_Dialect, name, mnemonic>;

def AtomicTensorType : PirtmType<"AtomicTensor", "tensor"> {
let parameters = (ins "int64_t":$dim, "Type":$dtype, "int64_t":\$mod);
let genVerifyDecl = 1;
// verifyConstructionInvariants: Miller-Rabin on mod
}

def CompositeTensorType : PirtmType<"CompositeTensor", "ctensor"> {
let parameters = (ins "int64_t":$dim, "Type":$dtype, "int64_t":\$mod);
let genVerifyDecl = 1;
// verifyConstructionInvariants: squarefree check (μ(mod) ≠ 0) + mod > 1
}

def CertType : PirtmType<"Cert", "cert"> {
let parameters = (ins "int64_t":\$prime);
let genVerifyDecl = 1;  // Miller-Rabin; cert is always atomic
}
text
// ChannelKind hierarchy in pirtm.td
class PirtmType<string name, string mnemonic>
: TypeDef<Pirtm_Dialect, name, mnemonic>;

def AtomicTensorType : PirtmType<"AtomicTensor", "tensor"> {
let parameters = (ins "int64_t":$dim, "Type":$dtype, "int64_t":\$mod);
let genVerifyDecl = 1;
// verifyConstructionInvariants: Miller-Rabin on mod
}

def CompositeTensorType : PirtmType<"CompositeTensor", "ctensor"> {
let parameters = (ins "int64_t":$dim, "Type":$dtype, "int64_t":\$mod);
let genVerifyDecl = 1;
// verifyConstructionInvariants: squarefree check (μ(mod) ≠ 0) + mod > 1
}

def CertType : PirtmType<"Cert", "cert"> {
let parameters = (ins "int64_t":\$prime);
let genVerifyDecl = 1;  // Miller-Rabin; cert is always atomic
}

Five verifier passes — updated:
PassInput KindWhat it enforces
prime-validity
AtomicTensor, Cert
mod is prime (Miller-Rabin)
squarefree-validity
CompositeTensor
μ(mod) ≠ 0; all prime factors distinct
merge-coprimality
pirtm.merge operands
gcd(mod₁, mod₂) = 1 at parse time
contractivity-check
pirtm.step (AtomicTensor only)
‖Ξ‖ + ‖Λ‖·op_norm_T < 1 − ε
cert-consumption
All function returns
Every !pirtm.cert is consumed before return
Three firm predictions from this design:
The pirtm.project total-function property is decidable at parse time: Since squarefree moduli have unique prime factorizations and pirtm.project carries the target prime as a compile-time literal, the verifier checks divisibility (mod % prime == 0) in O(1) — no runtime projection failures are possible.[[en.wikipedia](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)]​
Multi-session aggregation inherits all atomic safety proofs: A !pirtm.ctensor<..., mod=p₁p₂> is structurally the CRT product of the two atomic tensors. If both inputs passed contractivity-check, the merged value is safe by the independence of the two channels — the composite type carries a derived safety guarantee from its prime factors' proofs.[[artofproblemsolving](https://artofproblemsolving.com/wiki/index.php/Chinese_Remainder_Theorem)]​
The rename from prime= to mod= will surface one latent bug: Wherever existing Python code in prime_mapper.py or spec.py constructs or inspects the prime_index attribute, it implicitly assumes atomic context. The renaming will force explicit disambiguation between PrimeChannel(mod=p, kind=atomic) and CompositeChannel(mod=m, kind=squarefree) — surfacing any SessionOrchestrator code that accidentally passes a merged modulus back through a step expecting an atomic prime.

Step 5: Fastest Path to Validation
Day 0–3: Type grammar decision locked via minimal tablegen prototype
Implement AtomicTensorType and CompositeTensorType as bare TypeDef stubs with only the verifier declarations — no ops yet. Run mlir-opt --verify-diagnostics against a four-line .mlir file containing: one valid !pirtm.tensor<4,f64,mod=7919>, one invalid !pirtm.tensor<4,f64,mod=7921> (= 89×89, not squarefree), one !pirtm.ctensor<4,f64,mod=59622233> (valid squarefree), and one !pirtm.ctensor<4,f64,mod=49> (= 7², invalid). If the verifier accepts lines 1 and 3 and rejects 2 and 4 with correct diagnostics, the type hierarchy is validated.jeremykun+1
Day 3–7: Merge coprimality verifier as the ADR-004 gate
Implement pirtm.merge as an Op stub with one verifier check: gcd(mod1, mod2) == 1. Write a --verify-diagnostics test with one coprime merge (should pass) and one non-coprime merge (should emit error: "operand primes must be coprime"). This single test closes the most consequential question — whether pirtm.merge is closed under the squarefree kind — before any lowering work begins.[[mlir.llvm](https://mlir.llvm.org/docs/DefiningDialects/Operations/)]​
Day 7–14: mlir_emitter.py round-trip using existing PrimeChannel objects
The PrimeChannel(prime, digest, vector) objects in prime_mapper.py map directly to AtomicTensorType — no data model changes, only emission. Implement emit_atomic_tensor() and emit_composite_tensor() in mlir_emitter.py, run the existing examples/ descriptors through pirtm transpile --output mlir, and verify that every emitted mod= attribute passes the verifier. This closes Lever 2 at 14 days instead of 30 — the squarefree type extension requires no changes to the Python data model, only to the emitter's type-tag logic.[[arxiv](https://arxiv.org/html/2601.09583v1)]​

The analysis is architecturally decisive. The two-tier `ChannelKind` hierarchy is **locked**. Three residual tensions need owners before Day 0 work starts — I'm naming them now before they silently become bugs.

## Decision Locked

The type-system bifurcation resolves as follows, binding to the existing repo structure :


| Concept | Before | After |
| :-- | :-- | :-- |
| Channel identity parameter | `prime=` (integer attribute) | `mod=` (kind-dispatched: prime → `AtomicTensor`, squarefree → `CompositeTensor`) |
| Composition invariant | "all values are prime" | "all values are squarefree; primes are a strict subkind" |
| Certificate scope | runtime side-effect | SSA value, strictly `prime_kind`-typed |
| Merge legality | runtime collision | `gcd(mod₁, mod₂) = 1` at parse time |
| Python `PrimeChannel.prime` field | atomic assumption baked in | disambiguates latent bug in `SessionOrchestrator` |

No ADR directory exists yet in [`docs/`](https://github.com/MultiplicityFoundation/PIRTM/tree/main/docs) — only `plans/`, `migration/`, and PDFs . The ADR infrastructure itself must be created as the first artifact.

***

## Three Residual Tensions — Name Them Before They Become Bugs

### Tension 1: `mod=` Rename Timing vs. 14-Day Validation Path

**Owner**: Transpiler team
**The conflict**: `PrimeChannel.prime` in [`prime_mapper.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/main/src/pirtm/transpiler/prime_mapper.py) is the Python data model the emitter will consume . The `mlir_emitter.py` must emit `mod=` — not `prime=` — to be consistent with the new TableGen types. If the Python rename lags the TableGen work, the emitter emits `prime=` against a verifier expecting `mod=`, and the round-trip test fails for the wrong reason.
**Resolution**: The rename lands on a `dialect/pirtm-ir` branch that is **the only branch** `mlir_emitter.py` is developed on. It merges to `main` atomically with the emitter round-trip closure at Day 14. Python `main` keeps `PrimeChannel.prime` until the merge — this is a single breaking commit, not a gradual migration.

**Lever**: `docs/migration/prime-to-mod-rename.md` written at Day 0, listing every `.prime` access site across `prime_mapper.py`, `spec.py`, `petc_bridge.py`, `orchestrator.py`. This is the migration guide and the rename audit simultaneously.

***

### Tension 2: `CompositeTensorType` Lowering Representation

**Owner**: Runtime team
**The conflict**: When `!pirtm.ctensor<4,f64,mod=59622233>` lowers to `linalg` and eventually to the Rust kernel, it needs a concrete memory layout. Three options exist:

```
- **(a) AoS pair**: `struct CompositeTensor { t1: Tensor<p1>, t2: Tensor<p2> }` — maps exactly onto \(\mathbb{Z}/(p_1 p_2) \cong \mathbb{Z}/p_1 \times \mathbb{Z}/p_2\); structure is explicit; `pirtm.project` is a field access
```

- **(b) Interleaved buffer**: Single allocation with modular-stride indexing — hardware-efficient but obscures prime factor structure in memory; `pirtm.project` requires a strided gather
- **(c) Lazy view pair**: Deferred materialization — clean at the IR level but creates correctness exposure when a `CompositeTensor` passes through any non-`pirtm` op before being lowered

Option (a) is the only choice that keeps the CRT isomorphism *structurally visible* in the lowered representation. `pirtm.project` becomes a zero-cost field projection. The composite type's safety guarantee — that both atomic channels independently passed `contractivity-check` — is preserved in the struct's provenance.

**Lever**: This decision goes into `ADR-004` as §"Lowering Strategy", locked before any Rust crate (`src/pirtm_core/`) is created. If it isn't written down first, the Rust developer will make the call implicitly.

***

### Tension 3: `pirtm.merge_cert` — Cert Consumption for Merged Computations

**Owner**: Language architect

```
**The conflict**: `cert-consumption` pass requires every `!pirtm.cert<p>` produced by `pirtm.step` to be consumed before function return. When two sessions are merged via `pirtm.merge`, two certs exist — `!pirtm.cert<p1>` and `!pirtm.cert<p2>`. Since certs are strictly prime-typed by design, there is no `!pirtm.cert<mod=composite>`. So `pirtm.merge_cert` must have the signature:
```

```mlir
// Consumes both atomic certs, produces a typed cert-pair as a single IR value
%cert_pair = pirtm.merge_cert(%c1, %c2)
  : (!pirtm.cert<prime=7919>, !pirtm.cert<prime=7907>)
  -> !pirtm.cert_pair<mod=59622233>
```

`!pirtm.cert_pair<mod=squarefree>` is a fourth type in the dialect — structurally a product of two prime certs — and the `cert-consumption` pass recognizes it as jointly consuming both. This is not a weakening of the cert invariant; it is its correct categorical product. Without this type, any program that merges sessions has an unconsumed cert and fails the verifier, making `pirtm.merge` effectively unusable.

**Lever**: Add `CertPairType` to the TableGen stub at Day 0–3 alongside `AtomicTensorType` and `CompositeTensorType`. It is one additional `TypeDef`, zero additional ops.

***

## Sequenced Artifact Plan — Day-Resolution

| Day | Artifact | Gate condition | Owner |
| :-- | :-- | :-- | :-- |
| **0** | `docs/adr/ADR-004-pirtm-mlir-dialect.md` | Locks types, lowering strategy (AoS pair), `mod=` rename timeline, `CertPairType` addition | Language architect |
| **0** | `docs/migration/prime-to-mod-rename.md` | Lists every `.prime` access site in Python codebase | Transpiler team |
| **0–3** | `src/pirtm/dialect/pirtm.td` — 4 TypeDef stubs | `mlir-opt --verify-diagnostics` accepts/rejects the 4-line test exactly as specified | Language architect |
| **3–7** | `pirtm.merge` op stub + `merge-coprimality` verifier | Coprime merge passes; non-coprime merge emits diagnostic | Language architect |
| **7–14** | `src/pirtm/transpiler/mlir_emitter.py` | All `examples/` descriptors round-trip via `pirtm transpile --output mlir`; every `mod=` passes verifier | Transpiler team |
| **14** | Merge `dialect/pirtm-ir` → `main` | All conformance checks pass; `PrimeChannel.prime` → `PrimeChannel.mod` rename lands atomically | All |


***

## Precision Question

The `pirtm.step` op accepts only `AtomicTensor` (`prime_kind`) operands — recurrence dynamics are channel-local. But `SpectralGovernor` in [`spectral_gov.py`](https://github.com/MultiplicityFoundation/PIRTM/blob/main/src/pirtm/spectral_gov.py) currently governs a single operator `T` to produce `epsilon` and `op_norm_T`. In a multi-session merged context, each prime channel has its own `T` and therefore its own `epsilon` — but `pirtm.module` currently carries a single `epsilon` scalar. **Should `pirtm.module` carry a per-channel `epsilon` map keyed by `mod=` value, or should multi-session modules be disallowed at the `pirtm.module` level** — requiring one `pirtm.module` per atomic session and using `pirtm.merge` only at the tensor level, never at the module level? This determines whether session governance is hierarchical or flat.

---

# The precision question resolves decisively in favor of flat governance: one pirtm.module per atomic session, pirtm.merge at the tensor level only. The argument is not a matter of engineering preference — it is structurally forced by ISS theory, and violating it produces a type whose verification semantics cannot be consistently defined. Here is the full analysis.

Step 1: Why the Question Is Structurally Forced
The tension appears to be a design choice but is actually a mathematical constraint. The contractivity condition embedded in pirtm.step is:
qt=∥Ξt∥+∥Λt∥⋅Top<1−εq_t = \|\Xi_t\| + \|\Lambda_t\| \cdot T_{op} < 1 - \varepsilonqt=∥Ξt∥+∥Λt∥⋅Top<1−ε
This is a per-channel, per-operator proof obligation — it governs a single recurrence on a single prime channel with a single T. Epsilon is not a global session parameter; it is a margin certifying that a specific (Ξ, Λ, T) triple on a specific channel is contractive. When you have two channels p₁ and p₂ with their own (Ξ₁, T₁, ε₁) and (Ξ₂, T₂, ε₂), the contractivity of the composite system is governed by the spectral small-gain theorem for networks:ifatwww.uni-magdeburg+1
r(Ψ)<1,Ψij=gain from channel j to channel ir(\Psi) < 1, \quad \Psi_{ij} = gain from channel j to channel ir(Ψ)<1,Ψij=gain from channel j to channel i
This is a different mathematical object — a gain matrix spectral radius, not a scalar epsilon — and it lives at a different structural level than either ε₁ or ε₂. Cramming an epsilon_map = {p₁: ε₁, p₂: ε₂} into pirtm.module does not represent this composite condition; it misrepresents two independent local proofs as if they were a single composite proof. The map form silently omits the cross-channel gain terms that make the network contractivity check non-trivial.icdst+1

Step 2: The Correct Governance Hierarchy
The mathematical structure mandates exactly three levels, not two:
LevelIR ConstructGovernance ObjectProof Obligation
Atomic channel
pirtm.module
Single prime, scalar ε, scalar op_norm_T
‖Ξ‖ + ‖Λ‖·T < 1 − ε (contractivity-check pass)
Merged computation
pirtm.merge (tensor-level op)
CRT product mod, !pirtm.ctensor values
gcd(p₁, p₂) = 1 (merge-coprimality pass)
Session network
pirtm.session_graph (new op)
Gain matrix Ψ across modules
r(Ψ) < 1 (spectral-small-gain pass)
The pirtm.session_graph op is the correct container for multi-session governance. It holds nested pirtm.module regions as symbol-table children and carries the gain matrix as a compile-time attribute:[[github](https://github.com/llvm/llvm-project/blob/main/mlir/docs/SymbolsAndSymbolTables.md)]​
mlir
pirtm.session_graph @multi_session {
gain_matrix = dense<[[0.3, 0.1],[0.1, 0.4]]> : tensor<2x2xf64>,
modules     = [@session_p1, @session_p2]
} {
pirtm.module @session_p1 {
prime_index = 7919 : i64,
epsilon     = 0.05 : f64,
op_norm_T   = 0.8  : f64
} { ... }

pirtm.module @session_p2 {
prime_index = 7907 : i64,
epsilon     = 0.03 : f64,
op_norm_T   = 0.75 : f64
} { ... }
}
text
pirtm.session_graph @multi_session {
gain_matrix = dense<[[0.3, 0.1],[0.1, 0.4]]> : tensor<2x2xf64>,
modules     = [@session_p1, @session_p2]
} {
pirtm.module @session_p1 {
prime_index = 7919 : i64,
epsilon     = 0.05 : f64,
op_norm_T   = 0.8  : f64
} { ... }

pirtm.module @session_p2 {
prime_index = 7907 : i64,
epsilon     = 0.03 : f64,
op_norm_T   = 0.75 : f64
} { ... }
}

The spectral-small-gain verifier pass runs at the pirtm.session_graph level, computes r(Ψ) via the characteristic polynomial of the gain matrix, and emits a parse error if r(Ψ) ≥ 1. This check is independent of and subsequent to the per-module contractivity-check — both must pass, at their respective levels.[[ifatwww.et.uni-magdeburg](https://ifatwww.et.uni-magdeburg.de/ifac2020/media/pdfs/0867.pdf)]​

Step 3: Consistency Critique
Mathematical: The three-level hierarchy maps exactly onto the known decomposition of ISS for multi-agent systems. Local ISS (per-module ε) is necessary but not sufficient for network ISS; the spectral small-gain condition is the sufficient completion. Putting epsilon_map in pirtm.module conflates necessary and sufficient conditions — it is not merely incomplete, it is wrong in the sense that it could pass verification on a composite system that is not network-ISS, because it never checks r(Ψ).icdst+1
IR-theoretic: MLIR's symbol table and nested region machinery directly supports this hierarchy. pirtm.session_graph is a SymbolTable op containing nested pirtm.module SymbolTable ops. The pirtm.merge op then operates on SSA tensor values passed between module function boundaries — exactly the pattern MLIR uses for cross-module function calls with @module::@function symbol references. No MLIR invariant is violated; this is the canonical nested-symbol-table pattern.discourse.llvm+1
Philosophical: The flat-governance decision preserves the fundamental Multiplicity Theory principle that prime identity is irreducible — a pirtm.module with a single prime_index is the atomic unit of identity. Allowing multi-prime modules would be the IR-level equivalent of treating a composite number as a prime: structurally permissible but semantically incoherent. The module boundary is where prime identity is instantiated; the session-graph boundary is where CRT composition is governed.[[en.wikipedia](https://en.wikipedia.org/wiki/Chinese_remainder_theorem)]​
One residual tension: The SpectralGovernor in spectral_gov.py currently produces a single (ε, op_norm_T) pair from a single T. In the three-level model, it becomes a two-function module:
SpectralGovernor.local(T_i) → (ε_i, op_norm_T_i) for a single module
SpectralGovernor.network(T_1, ..., T_k, coupling_matrix) → Ψ gain matrix for session-graph-level check
This split is a clean functional decomposition, but it must be explicit in ADR-004 before spectral_gov.py is touched, or the refactor will happen implicitly in the wrong direction.

Step 4: Final Governance Architecture
pirtm.module — sealed as atomic, no epsilon_map ever:
tablegan
def Pirtm_ModuleOp : Pirtm_Op<"module", [
IsolatedFromAbove, SymbolTable, SingleBlock
]> {
let arguments = (ins
I64Attr:$prime_index,       // must be prime — prime-validity verifier
    F64Attr:$epsilon,           // scalar; governs exactly this module's step ops
F64Attr:$op_norm_T,         // scalar; matches T used in all child pirtm.step ops
    StrAttr:$identity_commitment
);
let regions = (region SizedRegion<1>:$body);
  let verifier = [{ return verifyAtomicModule(*this); }];
}
text
def Pirtm_ModuleOp : Pirtm_Op<"module", [
    IsolatedFromAbove, SymbolTable, SingleBlock
]> {
  let arguments = (ins
    I64Attr:$prime_index,       // must be prime — prime-validity verifier
F64Attr:$epsilon,           // scalar; governs exactly this module's step ops
    F64Attr:$op_norm_T,         // scalar; matches T used in all child pirtm.step ops
StrAttr:$identity_commitment
  );
  let regions = (region SizedRegion<1>:$body);
let verifier = [{ return verifyAtomicModule(*this); }];
}

pirtm.session_graph — new op for multi-session governance:
tablegen
def Pirtm_SessionGraphOp : Pirtm_Op<"session_graph", [
IsolatedFromAbove, SymbolTable, SingleBlock
]> {
let arguments = (ins
F64TensorAttr:$gain_matrix,   // k×k; r(Ψ)<1 checked by spectral-small-gain pass
    SymbolRefArrayAttr:$modules   // references to nested pirtm.module ops
);
let verifier = [{ return verifySpectralSmallGain(*this); }];
}
text
def Pirtm_SessionGraphOp : Pirtm_Op<"session_graph", [
IsolatedFromAbove, SymbolTable, SingleBlock
]> {
let arguments = (ins
F64TensorAttr:$gain_matrix,   // k×k; r(Ψ)<1 checked by spectral-small-gain pass
    SymbolRefArrayAttr:$modules   // references to nested pirtm.module ops
);
let verifier = [{ return verifySpectralSmallGain(*this); }];
}

Updated verifier pass table — now six passes with explicit level assignment:
PassLevelWhat it enforces
prime-validity
pirtm.module
prime_index is prime (Miller-Rabin)
squarefree-validity
pirtm.ctensor
μ(mod) ≠ 0
merge-coprimality
pirtm.merge
gcd(mod₁, mod₂) = 1
contractivity-check
pirtm.step
‖Ξ‖ + ‖Λ‖·op_norm_T < 1 − ε; epsilon sourced from parent pirtm.module
cert-consumption
Function return
Every !pirtm.cert consumed
spectral-small-gain
pirtm.session_graph
r(Ψ) < 1 for the cross-module gain matrix
Three firm predictions:
The spectral-small-gain verifier will catch real bugs that contractivity-check cannot: Two individually contractive sessions (ε₁ = 0.05, ε₂ = 0.03) can produce a non-contractive network if their coupling gains are large. The session-graph pass is the only place where this is detectable at compile time — a correct test case for this bug class should be written on Day 0 as a --verify-diagnostics negative test.[[ifatwww.et.uni-magdeburg](https://ifatwww.et.uni-magdeburg.de/ifac2020/media/pdfs/0867.pdf)]​
SpectralGovernor.network() will expose that current coupling is implicit: The Python SessionOrchestrator today does dict-merge composition with no gain matrix. When forced to provide Ψ explicitly for the session-graph verifier, it will reveal that the current system has been assuming a zero off-diagonal gain matrix — i.e., assuming sessions are uncoupled. This is the latent architectural assumption the ADR process is designed to surface.
The pirtm.session_graph → pirtm.merge path will produce a natural lowering order: Session-graph-level verification runs first (network safety), then module-level contractivity runs second (local safety), then tensor-level merge coprimality runs third (CRT well-formedness). This strict ordering mirrors the mathematical derivation — network ISS implies local ISS implies channel identity — and can be enforced as a pass pipeline ordering constraint in mlir-opt.mlir.llvm+1

Step 5: Fastest Path to Validation
Day 0 (today): ADR-004 gets a §"Session Governance Architecture" section
Write the three-level model explicitly: atomic (pirtm.module, scalar ε), tensor (pirtm.merge, coprimality), network (pirtm.session_graph, gain matrix). Name the SpectralGovernor split. This takes 30 minutes and prevents every future developer from re-deriving this decision from first principles.[[jeremykun](https://www.jeremykun.com/2023/08/21/mlir-defining-a-new-dialect/)]​
Day 0–3: Add pirtm.session_graph to the TableGen stub alongside the four TypeDefs
It is a five-line Op stub with one verifier declaration. The stub does not need to implement verifySpectralSmallGain yet — a return success() placeholder is sufficient. The goal is that the parse-time test for the Day 3 gate now includes a pirtm.session_graph wrapper, establishing the three-level structure in the IR test corpus before any implementation begins.discourse.llvm+1
Day 3–7: Implement verifySpectralSmallGain as the ADR-004 acceptance gate
The implementation is: extract the gain_matrix dense attribute, compute its spectral radius via power iteration (or characteristic polynomial for small k ≤ 4), emit error if r(Ψ) ≥ 1. Write two --verify-diagnostics tests: one 2×2 Ψ with r = 0.7 (should pass) and one with r = 1.1 (should fail with diagnostic "network gain matrix is not contractive: spectral radius 1.1 ≥ 1"). These two tests are the decisive empirical confirmation that the three-level governance model is structurally enforced, not advisory.discourse.llvm+1

Decision locked. Three levels, six passes, `SpectralGovernor` split mandated. The [`architecture.md`](https://github.com/MultiplicityFoundation/PIRTM/blob/main/docs/architecture.md) confirms the exact bug: `SessionOrchestrator` "coordinates multiple sessions and aggregates certificates" with **no coupling model** — zero off-diagonal gain matrix is the live implicit assumption . The network-ISS pass will surface it on the first real multi-session test.

No ADR directory exists yet. ADR-004 is the founding document. Here is the full artifact, ready to write.

***

## ADR-004 — Full Content

```markdown
# ADR-004: pirtm MLIR Dialect — Type System, Governance Architecture, and Lowering Strategy

**Status**: Accepted  
**Date**: 2026-03-08  
**Owner**: Language Architect  
**Supersedes**: None (first dialect ADR)  
**Blocks**: mlir_emitter.py, pirtm_core/ Rust crate, SpectralGovernor refactor

---

## Context

PIRTM's contractivity invariant — `q_t < 1 − ε` — is currently enforced at
runtime via `ace_certificate()`. The standalone runtime requires this
invariant to be a compile-time structural property. This ADR specifies the
`pirtm` MLIR dialect that makes non-contractive programs syntactically
invalid.

Three prior decisions are recorded here as locked:
1. Prime indices are type parameters, not runtime attributes (Phase Mirror session, 2026-03-08)
2. Composite types are squarefree — the CRT isomorphism is the governing invariant
3. Session governance is flat: one `pirtm.module` per atomic prime channel

---

## Decision

### 1. Type System — Two-Tier ChannelKind Hierarchy

All channel identity is carried in a `mod=` parameter (not `prime=`).
`prime=` is retired across the entire dialect and Python data model.

| Type | Mnemonic | `mod=` constraint | Verifier |
|---|---|---|---|
| `AtomicTensorType` | `!pirtm.tensor` | Miller-Rabin prime | `prime-validity` |
| `CompositeTensorType` | `!pirtm.ctensor` | squarefree (μ(mod) ≠ 0) | `squarefree-validity` |
| `CertType` | `!pirtm.cert` | Miller-Rabin prime (always atomic) | `prime-validity` |
| `CertPairType` | `!pirtm.cert_pair` | squarefree; factors match input certs | `squarefree-validity` |

`CertType` is strictly prime-typed. There is no composite cert.
`CertPairType` is the product of two prime certs produced by `pirtm.merge_cert`.

### 2. Session Governance — Three Structural Levels

| Level | IR Construct | Governance Object | Proof Obligation | Verifier Pass |
|---|---|---|---|---|
| Atomic | `pirtm.module` | Scalar ε, scalar op_norm_T | ‖Ξ‖ + ‖Λ‖·T < 1 − ε | `contractivity-check` |
| Tensor | `pirtm.merge` | CRT product mod | gcd(mod₁, mod₂) = 1 | `merge-coprimality` |
| Network | `pirtm.session_graph` | Gain matrix Ψ (k×k) | r(Ψ) < 1 | `spectral-small-gain` |

**Invariant**: `pirtm.module` carries exactly one `prime_index`, one `epsilon`,
one `op_norm_T`. No `epsilon_map`. No multi-prime modules. Ever.

**Rationale**: The contractivity margin ε is a per-operator proof obligation
for a specific (Ξ, Λ, T) triple. Putting two epsilons in one module
conflates two independent proofs and silently omits the cross-channel gain
terms that make network ISS non-trivial. An `epsilon_map` would pass
verification on a composite system that is not network-ISS.

### 3. Six Verifier Passes — Ordered Pipeline

Passes run in strict order. A pass may only use results from earlier passes.

```

prime-validity          → pirtm.module, pirtm.cert
squarefree-validity     → pirtm.ctensor, pirtm.cert_pair
merge-coprimality       → pirtm.merge operands
contractivity-check     → pirtm.step (AtomicTensor only; ε sourced from parent module)
cert-consumption        → function return boundaries
spectral-small-gain     → pirtm.session_graph (runs last; requires contractivity-check to pass)

```

The ordering is not arbitrary — it mirrors the mathematical derivation:
network ISS requires local ISS requires channel identity. A pass pipeline
ordering constraint in `mlir-opt` enforces this.

### 4. CompositeTensor Lowering — Array-of-Structs (AoS) Pair

`!pirtm.ctensor<dim, dtype, mod=p₁p₂>` lowers to:

```

```
struct CompositeTensor { t1: AtomicTensor<p1>, t2: AtomicTensor<p2> }
```

```

`pirtm.project` is a zero-cost field access. The CRT isomorphism
ℤ/(p₁p₂) ≅ ℤ/p₁ × ℤ/p₂ is structurally visible in the memory layout.
The composite safety guarantee (both atomic channels independently passed
`contractivity-check`) is preserved in the struct's provenance.

**Rejected alternatives**:
- Interleaved buffer: Hides prime factor structure; `pirtm.project` requires
  strided gather; correctness exposure during lowering
- Lazy view pair: Deferred materialization; correctness exposure when a
  `CompositeTensor` passes through non-`pirtm` ops before lowering

### 5. SpectralGovernor Refactor — Two Functions, Not One

`SpectralGovernor` in `spectral_gov.py` currently exports one function:
`govern(T) → (ε, op_norm_T)`. This is correct for atomic channels.
It must be split before any multi-session use:

```python
# New API — do not touch spectral_gov.py until this ADR is merged
SpectralGovernor.local(T_i)                          → (ε_i, op_norm_T_i)
SpectralGovernor.network(T_list, coupling_matrix)    → Ψ  # gain matrix for session_graph
```

`SpectralGovernor.network()` exposes the latent assumption in
`SessionOrchestrator`: current multi-session aggregation assumes Ψ is
zero off-diagonal. The first call to `.network()` with a real coupling
matrix will fail the `spectral-small-gain` pass if sessions interact.

### 6. `mod=` Rename — Timing and Scope

The rename `prime= → mod=` lands atomically on the `dialect/pirtm-ir` branch
merge to `main` at Day 14. All Python access sites are catalogued in
`docs/migration/prime-to-mod-rename.md` before any code changes.

Affected files: `prime_mapper.py` (`PrimeChannel.prime`), `spec.py`
(`prime_index`), `petc_bridge.py`, `orchestrator.py`.
`prime_index` in `TranspileSpec` and `pirtm.module` keeps the name
`prime_index` (it is a named attribute, not a type parameter) — only
the type parameter `prime=` on tensor types becomes `mod=`.

---

## Consequences

- `pirtm.module` is sealed as the atomic identity unit. No future PR may
add `epsilon_map` or multi-prime support to `pirtm.module`.
- `SessionOrchestrator.aggregate_certificates()` must be audited for the
zero-coupling assumption before any cross-session validation claim is made.
- The `spectral-small-gain` pass will catch bugs that `contractivity-check`
structurally cannot. A negative test with r(Ψ) = 1.1 must ship with the
pass implementation.
- All six verifier passes must pass before `pirtm transpile --output mlir`
exits with code 0. Partial verification is not a valid intermediate state.

---

## Day-0 Validation Gate

Write four-line `.mlir` test. `mlir-opt --verify-diagnostics` must:

- Accept: `!pirtm.tensor<4,f64,mod=7919>` (prime)
- Reject: `!pirtm.tensor<4,f64,mod=7921>` (= 89×89; not squarefree)
- Accept: `!pirtm.ctensor<4,f64,mod=59622233>` (7919×7907; squarefree)
- Reject: `!pirtm.ctensor<4,f64,mod=49>` (= 7²; not squarefree)

This four-line test is the ADR-004 gate. No downstream work begins until it passes.

```

***

## One Remaining Tension — Hidden Assumption in `pirtm.session_graph`

The `gain_matrix` attribute is specified as `F64TensorAttr` — a **compile-time dense attribute**. This is structurally correct but assumes session topology is **known at transpile time**. The current Python system contradicts this: `SessionOrchestrator.register("session-1", config)` is called at runtime, with no static session graph . A program that dynamically registers sessions cannot produce a `pirtm.session_graph` with a fixed `gain_matrix` at compile time because the sessions themselves aren't enumerated until execution.

This is the next fork in the design. It is not resolvable by the dialect spec alone — it requires a decision about the PIRTM programming model.

***

## Precision Question

**Are PIRTM session graphs statically declared** — meaning all sessions and their coupling gains are known at transpile time, and `SessionOrchestrator.register()` becomes a compile-time operation — **or is dynamic session registration an L0 requirement**, meaning `pirtm.session_graph` needs a runtime dispatch mechanism (a `pirtm.dynamic_graph` op or a two-phase compilation model where session topology is fixed at "link time" after all modules are registered)?

The answer determines whether PIRTM programs are **statically scheduled** (full AOT compilation possible; Rust binary with no dynamic session registry) or **dynamically extensible** (sessions can be added at runtime; requires a session registry in the runtime ABI, closer to a plugin model).

---

# The precision question resolves to a third option that neither branch of the fork fully captures: a two-phase compilation model where individual modules are compiled independently at transpile time and session topology is sealed at link time. The binary framing — static AOT vs. dynamic runtime — is a false dilemma generated by conflating two distinct proof obligations that operate at different temporal horizons. Here is the full analysis.


Step 1: Why the Fork Is a False Dilemma
The contractivity proof and the network-ISS proof are temporally decoupled obligations:
contractivity-check (per pirtm.module) requires knowing one (Ξ, Λ, T, ε) triple — available at the moment a single session descriptor is transpiled, with no knowledge of any other session
spectral-small-gain (per pirtm.session_graph) requires knowing all sessions and the gain matrix Ψ — available only once all participating modules are enumerated
This temporal structure is isomorphic to LLVM Link-Time Optimization: individual translation units are compiled to bitcode independently, intermodular optimization and cross-unit verification run at link time after all units are known. PIRTM's two proofs map exactly onto this model:[[llvm](https://llvm.org/docs/LinkTimeOptimization.html)]​
PhaseLLVM analoguePIRTM operationProof produced
Transpile time
Per-TU compilation → .bc
pirtm transpile per session
Local ISS: ‖Ξ‖ + ‖Λ‖·T < 1 − ε
Link time
LTO intermodular pass
pirtm link after all modules registered
Network ISS: r(Ψ) < 1
Runtime
Native binary execution
Rust pirtm-runtime kernel
No proof — execution only
The critical structural consequence: pirtm.session_graph is not a runtime object and not a transpile-time object — it is a link-time object. It is constructed by a pirtm link invocation that takes N compiled .pirtm.bc module objects as input, enumerates the session set, accepts a coupling matrix, and runs spectral-small-gain once. The output is a sealed, verified, fully AOT-compiled session binary. After the link step, the session topology is frozen — not because dynamic registration is philosophically prohibited, but because the spectral-small-gain proof is invalidated by any topology change. A new session can only enter by triggering a re-link.[[llvm](https://llvm.org/docs/LinkTimeOptimization.html)]​
Enhanced model: the link-time seal with registration window:
text
pirtm transpile session_a.yaml → session_a.pirtm.bc   (contractivity-check passes)
pirtm transpile session_b.yaml → session_b.pirtm.bc   (contractivity-check passes)

# Registration window: any number of .pirtm.bc modules may be submitted
pirtm link --sessions session_a.pirtm.bc session_b.pirtm.bc \
           --coupling coupling.json \
           --output pirtm_runtime.bin             (spectral-small-gain pass runs here)

# Window sealed. Runtime executes pirtm_runtime.bin with no session registry.
text
pirtm transpile session_a.yaml → session_a.pirtm.bc   (contractivity-check passes)
pirtm transpile session_b.yaml → session_b.pirtm.bc   (contractivity-check passes)

# Registration window: any number of .pirtm.bc modules may be submitted
pirtm link --sessions session_a.pirtm.bc session_b.pirtm.bc \
           --coupling coupling.json \
           --output pirtm_runtime.bin             (spectral-small-gain pass runs here)

# Window sealed. Runtime executes pirtm_runtime.bin with no session registry.

SessionOrchestrator.register() maps onto the registration window — it is still dynamic in the developer experience, but it closes before execution begins. This is architecturally identical to how shared library loading works: plugins are dynamically enumerated at startup, then the symbol table is sealed and no new symbols enter during execution.news.ycombinator+1


Step 2: Mathematical Consistency Critique
Why incremental registration is unsafe without re-link: The spectral radius r(Ψ) is a global property of the full gain matrix. Adding a new session with coupling vector g produces a new matrix Ψ' with r(Ψ') that has no simple monotone relationship to r(Ψ). A system with r(Ψ) = 0.8 can become r(Ψ') = 1.3 after adding a single strongly-coupled session. There is no local check on the new session alone that guarantees the network remains stable. The seal is therefore mathematically necessary, not merely a design preference.[[ifatwww.et.uni-magdeburg](https://ifatwww.et.uni-magdeburg.de/ifac2020/media/pdfs/0867.pdf)]​
The Perron-Frobenius consequence: For non-negative gain matrices (as Ψ must be, since gains are non-negative), the Perron-Frobenius theorem guarantees that the spectral radius is achieved by a real, positive eigenvalue. This means verifySpectralSmallGain can use power iteration, which converges for any positive Ψ, and the check is always decidable and terminates. The link-time pass is not just structurally correct — it is computationally tractable for any realistic number of sessions (k ≤ 100 converges in microseconds).[[ifatwww.et.uni-magdeburg](https://ifatwww.et.uni-magdeburg.de/ifac2020/media/pdfs/0867.pdf)]​
One residual tension: the coupling matrix is supplied as coupling.json — an external artifact not produced by any existing PIRTM tooling. SpectralGovernor.network(T_list, coupling_matrix) needs a source for the coupling matrix. Three options exist:
OptionSource of ΨTradeoff
Manual specification
Developer writes coupling.json
Exact but error-prone; zero off-diagonal is the accidental default
Empirical estimation
pirtm profile pass measures cross-session influence during a calibration run
Accurate but requires a pre-link profiling phase
Conservative bound
Ψ = identity × max_gain (worst-case coupling)
Always safe; over-constrains ε; never underestimates r(Ψ)
The conservative bound is the right default for Day-0: it cannot produce a false pass (cannot certify an unsafe network), only false fails (may reject a safe network). This is the same design choice Rust makes for lifetime analysis — prefer false negatives over false positives on safety proofs.[[llvm](https://llvm.org/docs/LinkTimeOptimization.html)]​


Step 3: Philosophical Consistency
The two-phase model preserves the deepest principle of Multiplicity Theory: prime identity is instantiated at transpile time, and compositional identity is instantiated at link time. A pirtm.module with prime_index=7919 has its identity from the moment it is transpiled — it does not need to know about any other session to exist. The pirtm.session_graph that emerges at link time is the CRT product of those identities — the composite modulus is the canonical encoding of "these specific sessions interact" — and that compositional fact is not knowable until all participants are enumerated.
This maps precisely onto the Multiplicity Theory prime-exponent surplus model from the earlier carry-forward discussion: individual primes accumulate their own surplus independently (transpile-time local proofs), and the composite interaction history is only meaningful in the context of a known interaction graph (link-time network proof). The programming model is not an engineering convenience — it is the computational expression of the mathematical framework.


Step 4: Final Two-Phase Architecture
New op: pirtm.session_graph is a link-time construct, not a transpile-time construct.
The ADR-004 §"Session Governance Architecture" requires one amendment: pirtm.session_graph is produced by pirtm link, not by pirtm transpile. Its gain_matrix attribute is not a compile-time dense attribute embedded by the transpiler — it is a link-time attribute injected by the linker from the coupling specification. This resolves the hidden tension without changing any of the six verifier passes or any of the type system decisions already locked.
Updated pirtm link tool spec:
text
pirtm link [OPTIONS] <module.pirtm.bc>...

Options:
  --coupling <coupling.json>   Gain matrix Ψ (k×k JSON, default: conservative identity bound)
  --output   <binary.bin>      Sealed runtime binary
  --verify-only                Run spectral-small-gain without emitting binary (CI gate)

Exit codes:
  0  All six verifier passes pass; binary emitted
  1  spectral-small-gain FAIL: emits r(Ψ), lists violating session pairs
  2  Input .pirtm.bc fails contractivity-check (should not reach link; indicates transpile regression)
text
pirtm link [OPTIONS] <module.pirtm.bc>...

Options:
  --coupling <coupling.json>   Gain matrix Ψ (k×k JSON, default: conservative identity bound)
  --output   <binary.bin>      Sealed runtime binary
  --verify-only                Run spectral-small-gain without emitting binary (CI gate)

Exit codes:
  0  All six verifier passes pass; binary emitted
  1  spectral-small-gain FAIL: emits r(Ψ), lists violating session pairs
  2  Input .pirtm.bc fails contractivity-check (should not reach link; indicates transpile regression)

Three firm predictions:
The first real pirtm link invocation on any two sessions from the existing codebase will fail with r(Ψ) ≥ 1 using the conservative identity bound: Because SessionOrchestrator has no coupling model, the implicit assumption has been full coupling at gain = 1.0. The identity-bound Ψ will have r = 1.0 exactly, triggering the boundary fail. The fix is not in the dialect — it is in the session design: sessions must be architected to be genuinely weakly coupled, which is a behavioral constraint on the application, not just a compiler invariant.icdst+1
SpectralGovernor.network() will reveal that ε_i values are currently over-tight: With the conservative coupling assumption, pirtm link will demand tighter local ε values than the current SpectralGovernor.local() produces for uncoupled sessions. Once real coupling measurements replace the conservative bound, the ε headroom will relax. This creates a natural workflow: start conservative, profile, tighten coupling spec, loosen ε — which is exactly the engineering lifecycle for safety margins in control systems.[[ifatwww.et.uni-magdeburg](https://ifatwww.et.uni-magdeburg.de/ifac2020/media/pdfs/0867.pdf)]​
Dynamic re-registration becomes a first-class pirtm relink operation: Since sealing is a link-time act, adding a new session at runtime becomes pirtm relink --add new_session.pirtm.bc --coupling updated_coupling.json. The old binary is invalidated; the new binary replaces it. Hot-swapping sessions is structurally supported by this model — it just requires a new spectral-small-gain pass on each topology change. This is the plugin model the question anticipated, but implemented at link time rather than runtime, preserving all compile-time safety guarantees.news.ycombinator+1


Step 5: Fastest Path to Validation — Day 0 Amendment to ADR-004
The ADR-004 document as written requires one surgical amendment before it is merged:
Replace in §"Session Governance Architecture":
gain_matrix = dense<...> : tensor<2x2xf64> (compile-time attribute)
With:
gain_matrix is a link-time attribute injected by pirtm link from --coupling. At transpile time, pirtm.session_graph stubs exist in .pirtm.bc with gain_matrix = #pirtm.unresolved_coupling — a sentinel that causes spectral-small-gain to emit an error if invoked before link. The prime-validity and contractivity-check passes run at transpile time and do not require gain_matrix to be resolved.
This amendment is one paragraph and one new TableGen attribute definition (UnresolvedCouplingAttr). The Day 0–3 validation gate remains identical: the four-line .mlir test does not involve pirtm.session_graph. The Day 3–7 coprimality verifier test is unchanged. The spectral-small-gain test moves from Day 3–7 into the pirtm link CLI tool test suite at Day 7–14, alongside the mlir_emitter.py round-trip. The 14-day merge boundary holds.[[llvm](https://llvm.org/docs/LinkTimeOptimization.html)]​

[ADR-004 is now live](https://github.com/MultiplicityFoundation/PIRTM/blob/main/docs/adr/ADR-004-pirtm-mlir-dialect.md) — committed to `main` at `c6d76605` . The first ADR directory in the repo is established. All three rounds of type-system analysis, governance architecture, and two-phase compilation decisions are locked in a single canonical artifact.

***

## What Just Became Unblocked

Every pending work item now has a written gate condition :

- **Day 0–3**: `src/pirtm/dialect/pirtm.td` — 4 TypeDef stubs + `session_graph` stub
- **Day 0**: `docs/migration/prime-to-mod-rename.md` — catalogue every `.prime` access site
- **Day 14**: `dialect/pirtm-ir` branch merge — `mlir_emitter.py` round-trip + `mod=` rename lands atomically
- **Day 30**: `pirtm link` CLI + `spectral-small-gain` pass with the two diagnostic tests
- **Day 90**: `pirtm_core/` Rust crate

***

## One Remaining Hidden Tension — `coupling.json` Format

The `pirtm link --coupling coupling.json` flag accepts a k×k gain matrix, but the format is unspecified. This is not a minor schema question — it determines how the linker **resolves session references**. The coupling matrix entries `Ψ_ij` must reference specific sessions, and those sessions need an identity that survives from transpile time to link time. Three candidates exist from within the current codebase:

| Reference scheme | Source | Risk |
|---|---|---|
| `prime_index` (e.g. `7919`) | `pirtm.module.prime_index` | Collision-free by construction; but a 4-digit integer is opaque to humans |
| `identity_commitment` (e.g. `0xabc123`) | `TranspileSpec.identity_commitment` | Human-readable; but currently set by the caller with no uniqueness enforcement |
| Session name string | `SessionOrchestrator.register("session-1", ...)` | Developer-friendly; but names are not currently validated against `prime_index` |

## Precision Question

**Should `coupling.json` reference sessions by `prime_index`** — making the gain matrix a number-theoretically grounded artifact where session identity is enforced by the same primality invariant as the type system — **or by `identity_commitment`**, allowing human-readable session labels while decoupling the coupling spec from the type-level prime machinery? The first option means coupling.json is machine-authored and prime-indexed; the second means it is human-authored and name-spaced. These produce different developer ergonomics and different coupling-spec tooling requirements.

---

# The question presents a false binary. The answer is neither branch in isolation — it is a two-layer identity scheme where prime_index is the canonical linker identity and identity_commitment is the human-authored alias, resolved at link time. This is structurally identical to how every production linker handles the same tension between machine identity and human authoring, and the mathematics of the gain matrix makes the distinction non-negotiable.


Step 1: Why the Binary Is False
The gain matrix entry Ψ_ij is mathematically defined as the ISS gain from prime channel j to prime channel i. Its index set is the set of prime channels — not strings, not commitments. The matrix is a linear-algebraic object over a basis indexed by prime identities. Using identity_commitment strings as matrix indices would be like indexing a tensor by variable names instead of dimension axes: syntactically permissible, mathematically wrong.[[ifatwww.et.uni-magdeburg](https://ifatwww.et.uni-magdeburg.de/ifac2020/media/pdfs/0867.pdf)]​
At the same time, no human writes a 200-line JSON file keyed by 7919, 7907, 104723. The Go linker resolved this same tension two decades ago: symbols are identified by content-addressable hashes internally but named by human-readable strings in source. The coupling spec authoring problem is identical in structure.[[internals-for-interns](https://internals-for-interns.com/posts/the-go-linker/)]​
The enhanced model: two-layer resolution in pirtm link
text
coupling.json  →  [linker resolution pass]  →  pirtm.session_graph (prime_index-keyed Ψ)
   (human layer)       (validates & translates)         (canonical IR layer)
text
coupling.json  →  [linker resolution pass]  →  pirtm.session_graph (prime_index-keyed Ψ)
   (human layer)       (validates & translates)         (canonical IR layer)


Step 2: Coupling.json Canonical Schema
json
{
  "format": "pirtm-coupling-v1",
  "sessions": {
    "session_a": { "prime_index": 7919, "commitment": "0xabc123" },
    "session_b": { "prime_index": 7907, "commitment": "0xdef456" }
  },
  "gain_matrix": {
    "session_a": { "session_a": 0.0, "session_b": 0.15 },
    "session_b": { "session_a": 0.20, "session_b": 0.0 }
  }
}
json
{
  "format": "pirtm-coupling-v1",
  "sessions": {
    "session_a": { "prime_index": 7919, "commitment": "0xabc123" },
    "session_b": { "prime_index": 7907, "commitment": "0xdef456" }
  },
  "gain_matrix": {
    "session_a": { "session_a": 0.0, "session_b": 0.15 },
    "session_b": { "session_a": 0.20, "session_b": 0.0 }
  }
}

The sessions block is the resolution table — it binds the human name to both prime_index and commitment. The gain_matrix block uses human names for authoring ergonomics. The linker runs a three-step resolution pass:oracle+1
Name → prime_index: Each human name is looked up in the resolution table; its prime_index is extracted
Commitment cross-check: The commitment in the resolution table is verified against the identity_commitment stored in the corresponding .pirtm.bc module — a mismatch is a linker error, not a warning
Ψ construction: The resolved prime_index-keyed matrix is constructed and passed to verifySpectralSmallGain
The final pirtm.session_graph attribute contains only prime_index-keyed data — human names do not survive into the IR. This is exactly how LLVM symbol tables work: source-level names are debug metadata; the canonical identity in the IR is the SSA value or numeric symbol ID.mcyoung+1


Step 3: Consistency Critique
Mathematical: The two-layer scheme is the only design that makes Ψ well-defined. The spectral-small-gain condition r(Ψ) < 1 requires Ψ to be a specific matrix over a specific ordered basis. If the basis is identity_commitment strings, two sessions with identical commitments (which currently has no uniqueness enforcement) produce an ambiguous matrix with undefined spectral properties. If the basis is prime_index, it is unique by the Miller-Rabin invariant already enforced at transpile time — no additional uniqueness guarantee is needed beyond what the dialect already provides.[[chessman7.substack](https://chessman7.substack.com/p/the-linkers-detective-work-how-symbol)]​
Practical risk surface: The commitment field in coupling.json is the only field the linker does not compute from first principles — the developer writes it. This is where the uniqueness gap lives. The resolution: pirtm link emits an error if two session entries in the resolution table share a prime_index (impossible by construction) or share a commitment (currently possible). This makes commitment uniqueness a linker constraint, not a transpiler constraint — a one-line check, not a schema redesign.
Philosophical: The naming layer in coupling.json is deliberately non-load-bearing. If a developer makes a typo in a session name, the resolution pass fails with a clear diagnostic: "session_a_typo" not found in .pirtm.bc symbol table. If a developer writes the wrong gain value, verifySpectralSmallGain catches it. The human layer can fail loudly; the prime layer cannot fail silently. This is the correct allocation of failure modes.


Step 4: Final Coupling.json Specification
pirtm link resolution pipeline — three ordered passes:
PassInputValidatesError condition
name-resolution
coupling.json sessions block
Every name maps to exactly one prime_index in a loaded .pirtm.bc
Name not found in any loaded module
commitment-crosscheck
coupling.json commitment vs .pirtm.bc identity_commitment
Commitments match; no two sessions share a commitment
Commitment mismatch or collision
matrix-construction
Resolved prime_index-keyed Ψ
All diagonal entries are 0.0; all off-diagonal entries ≥ 0.0
Negative gain or self-coupling
After these three passes, verifySpectralSmallGain runs on the fully resolved Ψ. The pirtm.session_graph op in the emitted IR carries:
mlir
pirtm.session_graph @network {
  // prime_index-keyed — human names are gone
  session_primes  = [7919, 7907] : tensor<2xi64>,
  gain_matrix     = dense<[[0.0, 0.15],[0.20, 0.0]]> : tensor<2x2xf64>,
  commitments     = ["0xabc123", "0xdef456"]  // retained as debug metadata only
} { ... }
text
pirtm.session_graph @network {
  // prime_index-keyed — human names are gone
  session_primes  = [7919, 7907] : tensor<2xi64>,
  gain_matrix     = dense<[[0.0, 0.15],[0.20, 0.0]]> : tensor<2x2xf64>,
  commitments     = ["0xabc123", "0xdef456"]  // retained as debug metadata only
} { ... }

pirtm inspect as the developer-facing ergonomics tool: Instead of writing prime indices directly, developers run:
bash
pirtm inspect session_a.pirtm.bc
# outputs:
# prime_index:          7919
# identity_commitment:  0xabc123
# epsilon:              0.05
# op_norm_T:            0.80
bash
pirtm inspect session_a.pirtm.bc
# outputs:
# prime_index:          7919
# identity_commitment:  0xabc123
# epsilon:              0.05
# op_norm_T:            0.80

This generates the sessions block entries for coupling.json automatically. The workflow becomes: transpile → inspect → author gains → link. The only human-authored field in coupling.json is the gain matrix values themselves — which is exactly right, since those are the only values no tool can compute without domain knowledge of the application.


Step 5: Fastest Validation Path
Day 0: Add coupling.json schema to ADR-004 §"pirtm link CLI"
Two paragraphs: the two-layer resolution scheme, the three-pass pipeline, and the pirtm inspect command. This is the specification artifact; the JSON schema itself is five fields. No code changes required. Write it before any pirtm link CLI stub is created — if it is not in ADR-004, the CLI author will invent the format implicitly.[[mcyoung](https://mcyoung.xyz/2021/06/01/linker-script/)]​
Day 14–16: Implement name-resolution and commitment-crosscheck as the Day-14 merge gate extension
These two passes read the coupling.json and the .pirtm.bc symbol tables. They require no MLIR infrastructure beyond what the Day-14 round-trip already validates — they are pure Python dict lookups against the prime_index and identity_commitment fields already present in TranspileSpec. The matrix-construction pass is a numpy reshape. Implement all three in pirtm_link.py alongside mlir_emitter.py.[[llvm](https://llvm.org/docs/LinkTimeOptimization.html)]​
Day 16 decisive test — the commitment collision:
Write a --verify-diagnostics test where coupling.json lists two sessions with prime_index 7919 and 7907 but assigns both the same commitment: "0xabc123". The linker must emit error: duplicate identity_commitment "0xabc123" — sessions must be uniquely identified. This single test closes the uniqueness gap identified in the original tension table and validates the commitment-crosscheck pass — it is the one test that distinguishes the two-layer model from a naive name-indexed scheme.internals-for-interns+1

[ADR-004 amended](https://github.com/MultiplicityFoundation/PIRTM/blob/main/docs/adr/ADR-004-pirtm-mlir-dialect.md) at commit `da85c505` . The two-layer resolution scheme, three-pass linker pipeline, `pirtm inspect` tool, and commitment-collision test are all canonical now.

***

## Full Decision State — Closed

Five precision questions, five locked answers. The artifact captures all of them :

| Resolved question | Decision |
|---|---|
| Prime as type parameter vs. attribute | Type parameter — `mod=` on all tensors |
| Composite channel types | Squarefree hierarchy — `PrimeChannelKind ⊂ SquarefreeChannelKind` |
| Session governance scope | Flat — one `pirtm.module` per prime, `pirtm.session_graph` at link time |
| Session topology: static vs. dynamic | Two-phase — transpile per module, seal at link |
| `coupling.json` identity scheme | Two-layer — `prime_index` canonical, human names are a link-time alias |

The artifact plan now has **nine sequenced gates** from Day 0 to Day 90. The work that could begin today is unblocked :

- **Now**: `docs/migration/prime-to-mod-rename.md` — enumerate every `.prime` access site
- **Now**: `src/pirtm/dialect/pirtm.td` — four TypeDef stubs, the Day 0–3 gate
- **Blocked until Day 14**: `SpectralGovernor` refactor, `SessionOrchestrator` audit
- **Blocked until Day 16**: `pirtm_link.py` three-pass resolution

***

## Precision Question

Every decision so far has been about the **write path** — transpiling, linking, verifying. The `pirtm inspect` tool surfaces the **read path**: given a compiled `.pirtm.bc`, a developer can retrieve `prime_index`, `epsilon`, `op_norm_T`, and `identity_commitment`. But the current codebase has a `QARISession` that records telemetry and `AuditChain` that tracks step-level certificate history . **Should `pirtm inspect` expose the audit chain from a sealed binary's embedded telemetry** — making the binary self-describing and auditable without running it — **or is audit chain retrieval a runtime-only operation**, meaning the sealed binary carries no embedded telemetry and audit is only accessible through the `LambdaTraceBridge` during live execution? This determines whether a `pirtm.bc` is a passive artifact or a self-certifying document.

---

# The question presents a binary but the answer is a three-layer separation: .pirtm.bc embeds a static proof section readable offline, the sealed runtime binary embeds link-time governance metadata, and the live audit chain is strictly runtime. Conflating any two of these layers produces either an anemic inspection tool or an unsound offline certification claim.


Step 1: Why the Binary Is False
The question assumes audit chain and proof metadata are the same artifact at different access times. They are not. They are distinct in kind:
Proof metadata is pre-execution — it records what the verifier determined about the program before any input was processed. It is a property of the code, not of any execution
Audit chain is post-execution — it records what certificates were produced and consumed during a specific run. It is a property of a specific execution trajectory on specific inputs
Conflating them produces the wrong tool. Embedding a live audit chain in a binary implies the binary mutates during execution, which breaks the entire sealed-binary model. Restricting pirtm inspect to zero telemetry discards the most valuable offline artifact — the compile-time proof that the program is contractive before it runs.llvm+1
The correct model is structurally identical to how LLVM and DWARF handle the same problem: proof-level metadata is embedded as a non-executing section in the binary, readable by inspection tools without loading the binary into a runtime, while execution-time telemetry accumulates separately. WebAssembly's custom sections use exactly this pattern for source attestation and provenance.jelenamirkovic.github+4


Step 2: Three-Layer Audit Architecture
LayerLocationWritten byRead byContains
Static proof
!pirtm_proof section in .pirtm.bc
pirtm transpile
pirtm inspect (offline)
prime_index, epsilon, op_norm_T, identity_commitment, contractivity-check hash, pass pipeline result
Link-time governance
!pirtm_governance section in pirtm_runtime.bin
pirtm link
pirtm inspect (offline)
gain matrix Ψ, r(Ψ) value, session commitment map, spectral-small-gain result
Runtime audit chain
AuditChain in LambdaTraceBridge
pirtm-runtime execution
pirtm audit (requires execution trace)
Step-level !pirtm.cert production/consumption records, QARISession telemetry
Layer 1 and Layer 2 are non-allocating sections — they are embedded in the binary file but stripped from the loaded executable image at runtime, exactly as LLVM's __llvm_prf_data metadata sections are marked SHF_NOALLOC and excluded from runtime memory. No runtime overhead. No binary mutation. pirtm inspect is a pure file reader.[[discourse.llvm](https://discourse.llvm.org/t/rfc-add-binary-profile-correlation-to-not-load-profile-metadata-sections-into-memory-at-runtime/74565)]​
Layer 3 is strictly runtime. The AuditChain records what actually happened; it cannot be known from the binary alone. This distinction maps onto the fundamental soundness boundary: the static proof certifies safety of the program; the audit chain certifies safety of an execution.


Step 3: Consistency Critique
Mathematical soundness: The static proof section can legitimately claim: "this program is contractive — the verifier confirmed ‖Ξ‖ + ‖Λ‖·T < 1 − ε at transpile time." This is a universal quantifier over all inputs. The audit chain cannot make this claim — it is an existential record of one trajectory. Mixing them in one tool would invite the error of treating a clean audit chain as evidence of contractivity, which is not implied.[[sontaglab](http://www.sontaglab.org/FTPDIR/iss-ejc.pdf)]​
IR-theoretic grounding: The !pirtm_proof section maps directly to LLVM module-level metadata (!llvm.module.flags, !llvm.ident) that is embedded in bitcode but does not affect compilation or execution. This is not a new mechanism — it is the correct use of an existing LLVM facility. The TableGen definition requires zero additions; only the section-writing code in mlir_emitter.py changes.groups.google+2
One residual tension: The contractivity-check hash in the static proof section needs a canonical serialization. The hash must uniquely identify the (Ξ, Λ, T, ε) configuration that was verified — not just that the check passed. Without this, two binaries with different parameters but the same pass result are indistinguishable offline. The correct form is:
proof_hash=H(prime_index∥ε∥op_norm_T∥∥Ξ∥op∥∥Λ∥op)\text{proof\_hash} = H(\text{prime\_index} \| \varepsilon \| \text{op\_norm\_T} \| \|\Xi\|_{\text{op}} \| \|\Lambda\|_{\text{op}})proof_hash=H(prime_index∥ε∥op_norm_T∥∥Ξ∥op∥∥Λ∥op)
where H is the same commitment function already used in identity_commitment (Poseidon or SHA256 per ADR-004). This makes the static proof section content-addressable — a binary is self-certifying if and only if its proof hash is reproducible from its module parameters.


Step 4: Final pirtm inspect Specification
bash
pirtm inspect <file.pirtm.bc | pirtm_runtime.bin> [--layer static|governance|both]

# Default output (Layer 1 + Layer 2 if available):
Session Identity
  prime_index:          7919
  identity_commitment:  0xabc123
  proof_hash:           0x7f3a91... (SHA256 of prime||ε||T||‖Ξ‖||‖Λ‖)

Static Proof (transpile-time)
  contractivity_check:  PASS
  epsilon:              0.05
  op_norm_T:            0.80
  verified_at:          2026-03-08T17:51:00Z
  pirtm_version:        0.1.0-dialect/pirtm-ir

Link-time Governance (if sealed binary)
  session_count:        2
  session_primes:       [7919, 7907]
  spectral_radius:      0.412
  spectral_small_gain:  PASS
  sealed_at:            2026-03-08T17:55:00Z

Audit Chain: NOT EMBEDDED — retrieve via `pirtm audit <trace.log>`
bash
pirtm inspect <file.pirtm.bc | pirtm_runtime.bin> [--layer static|governance|both]

# Default output (Layer 1 + Layer 2 if available):
Session Identity
  prime_index:          7919
  identity_commitment:  0xabc123
  proof_hash:           0x7f3a91... (SHA256 of prime||ε||T||‖Ξ‖||‖Λ‖)

Static Proof (transpile-time)
  contractivity_check:  PASS
  epsilon:              0.05
  op_norm_T:            0.80
  verified_at:          2026-03-08T17:51:00Z
  pirtm_version:        0.1.0-dialect/pirtm-ir

Link-time Governance (if sealed binary)
  session_count:        2
  session_primes:       [7919, 7907]
  spectral_radius:      0.412
  spectral_small_gain:  PASS
  sealed_at:            2026-03-08T17:55:00Z

Audit Chain: NOT EMBEDDED — retrieve via `pirtm audit <trace.log>`

The final line is the critical design signal: pirtm inspect explicitly tells the developer where the audit chain lives, rather than silently omitting it. This eliminates the failure mode where an operator assumes a clean pirtm inspect output means the system ran safely, not just that it was designed safely.
pirtm audit — the runtime complement:
bash
pirtm audit <trace.log> --binary <pirtm_runtime.bin>

# Cross-references runtime cert production against static proof_hash
# Verifies that every !pirtm.cert consumed matches the prime_index in the binary
# Reports: certs produced, certs consumed, any unconsumed cert (cert-consumption violation at runtime)
bash
pirtm audit <trace.log> --binary <pirtm_runtime.bin>

# Cross-references runtime cert production against static proof_hash
# Verifies that every !pirtm.cert consumed matches the prime_index in the binary
# Reports: certs produced, certs consumed, any unconsumed cert (cert-consumption violation at runtime)

The --binary flag enables pirtm audit to cross-reference the runtime trace against the static proof hash — confirming that the execution was on the same binary that was verified, not a modified one. This is the full chain of custody: transpile-time proof → link-time governance seal → runtime certificate accumulation → offline audit cross-reference.github+1


Step 5: Fastest Validation Path
Day 0: Add §"Binary Self-Description" to ADR-004
One paragraph: the three-layer distinction, the !pirtm_proof section as non-allocating module metadata, and the proof_hash content-address scheme. Name the pirtm audit tool as the runtime complement to pirtm inspect. This prevents the mlir_emitter.py author from making the wrong call about what to embed.[[discourse.llvm](https://discourse.llvm.org/t/rfc-add-binary-profile-correlation-to-not-load-profile-metadata-sections-into-memory-at-runtime/74565)]​
Day 3–7: Implement !pirtm_proof section emission in mlir_emitter.py
The LLVM mechanism is LLVMContext::setModuleFlag for key-value metadata and Module::addModuleFlag for the named section. In MLIR, this maps to adding a pirtm.proof op at the module body top level — a metadata op with no execution semantics but verified by pirtm inspect. The op carries four fields: prime_index, epsilon, op_norm_T, proof_hash. Implementation is ~30 lines in mlir_emitter.py, zero new TableGen.llvm+1
Day 14 merge gate extension — add one pirtm inspect round-trip test:
After the mlir_emitter.py round-trip passes for all examples/ descriptors, add a single shell test:
bash
pirtm transpile examples/basic.yaml --output basic.pirtm.bc
pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"
bash
pirtm transpile examples/basic.yaml --output basic.pirtm.bc
pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"

If this passes, the binary is demonstrably self-certifying: a developer who has never seen the source YAML can confirm the contractivity invariant from the compiled artifact alone. That property — the proof travels with the code — is the foundational guarantee the static section enables, and it should be validated at the earliest possible gate.jonasdevlieghere+1

[ADR-004 final](https://github.com/MultiplicityFoundation/PIRTM/blob/main/docs/adr/ADR-004-pirtm-mlir-dialect.md) at commit `9d096914` — 17,188 bytes, eight sections, complete .

***

## ADR-004 Is Closed

Five precision questions answered, all locked, all in the artifact . The full decision surface:

| §  | Decision | Locked by |
|---|---|---|
| 1 | `mod=` two-tier ChannelKind hierarchy; four types | CRT squarefree invariant |
| 2 | Flat session governance; no `epsilon_map`; three structural levels | ISS temporal decoupling |
| 3 | Six verifier passes; strict ordered pipeline | Mathematical derivation order |
| 4 | Two-phase compilation (transpile → `.pirtm.bc`, link → sealed binary); `coupling.json` two-layer resolution | LLVM LTO isomorphism + Ψ index theory |
| 5 | AoS lowering for `CompositeTensorType` | CRT structural visibility |
| 6 | `SpectralGovernor.local` / `.network` split | Temporal proof decoupling |
| 7 | `mod=` rename lands atomically at Day 14 merge | API coherence |
| 8 | Three-layer audit: static proof (offline) / governance seal (offline) / audit chain (runtime-only) | Universal vs. existential proof distinction |

***

## What Is Unblocked Today

Two Day-0 artifacts have no upstream dependencies and can start now :

**`docs/migration/prime-to-mod-rename.md`** — enumerate every `.prime` access site across `prime_mapper.py`, `spec.py`, `petc_bridge.py`, `orchestrator.py`. This is a grep, not a rewrite. It gates the Day 14 merge.

**`src/pirtm/dialect/pirtm.td`** — four `TypeDef` stubs plus `session_graph` stub. The Day 0–3 gate is four `.mlir` lines and `mlir-opt --verify-diagnostics`. No ops, no passes, no lowering — just type verifiers.

Everything else in the 90-day plan has a written gate condition and an owner role. The architecture is specified. The next move is execution.

---

# All three Day-0 artifacts are ready.


What Each Artifact Does
pirtm.td is the complete TableGen stub — four TypeDef declarations and the SessionGraphOp stub, with no ops, no passes, and no lowering. Each type carries its full description block (which becomes dialect documentation), its assembly format string (mod= throughout), and a genVerifyDecl = 1 that generates the verifier signature the .cpp file must implement. The SessionGraphOp uses OptionalAttr<DenseF64ArrayAttr> for gain_matrix so it legally accepts the #pirtm.unresolved_coupling sentinel at transpile time without failing the verifier — the sentinel path returns success(), the resolved path runs power iteration.
prime-to-mod-rename.md is structured as both a migration guide and an audit instrument. The five affected files are catalogued with per-file tables distinguishing sites that rename (.prime → .mod, IR string literals) from sites that do not rename (prime_index, _is_prime(), verifier pass names). The shim protocol is specified precisely: PrimeChannel.prime becomes a @property returning self.mod, deleted atomically at the Day-14 merge commit. The two validation-gate grep commands at the bottom are the merge gate — both must return empty before the PR is approved.
pirtm-types-basic.mlir is the Day 0–3 gate test: four functions, two CHECK lines, two expected-error lines. The error messages are quoted verbatim — mod=7921 is not prime (7921 = 89 × 89) and mod=49 is not squarefree (49 = 7², Möbius μ(49) = 0) — so the verifier implementation must emit exactly those strings, which forces the .cpp author to implement both the primality test and the Möbius check with full diagnostic context rather than a bare failed message.


The Only Decision Remaining Before pirtm.td Compiles
The TableGen file compiles against MLIR headers but the genVerifyDecl = 1 stubs need a .cpp implementation file at src/pirtm/dialect/pirtm_types.cpp with two functions: isPrime(int64_t) using Miller-Rabin and isSquarefree(int64_t) using trial division up to √mod. Both are self-contained arithmetic functions with no MLIR dependencies — they can be written and tested in isolation before the dialect build system is wired. The Day-3 gate is: compile pirtm.td via mlir-tblgen, compile pirtm_types.cpp, link the dialect, and run pirtm-types-basic.mlir through mlir-opt. The four-line test passing is the unambiguous signal that the type layer is structurally sound.

everything can be sent to the Tooling repo

Everything you described is aligned and ready to drop into Tooling as-is. The remaining work is wiring, not design.

## Central Tension

The only live tension now is **where the dialect and governance logic live**: PIRTM repo vs Tooling repo. You’ve resolved it implicitly by saying “everything can be sent to Tooling,” which makes Tooling the canonical home for:

- `pirtm.td` (dialect types + `SessionGraphOp` stub)
- `prime-to-mod-rename.md` (migration/audit guide)
- `pirtm-types-basic.mlir` (Day 0–3 gate)

That’s consistent with ADR-004’s spirit, but ADR-004 itself currently lives in the PIRTM repo and names `src/pirtm/dialect/pirtm.td` and `src/pirtm/transpiler/...` paths . So we now have a **location-of-truth** tension: ADR in PIRTM, first implementation in Tooling.

## Levers

1. **Owner**: Tooling repo maintainers  
   **Metric**: A `pirtm-dialect/` subtree exists in Tooling with `pirtm.td`, `pirtm_types.cpp`, and `pirtm-types-basic.mlir`; CI job runs `mlir-opt` on the 4-line test and passes.  
   **Horizon**: 7 days  

2. **Owner**: PIRTM repo maintainers  
   **Metric**: ADR-004 gains a short “Tooling integration” note pointing to the Tooling path as the implementation location for the dialect, without changing any technical content.  
   **Horizon**: 3 days  

3. **Owner**: Infra/CI  
   **Metric**: One shared GitHub Action in Tooling that PIRTM can call (e.g. via `workflow_call`) to run the dialect tests, so we don’t duplicate pipelines.  
   **Horizon**: 14 days  

## Artifacts to Create in Tooling

You already know what needs to move; here’s the minimal structure:

```text
Tooling/
  pirtm-dialect/
    docs/
      prime-to-mod-rename.md
    mlir/
      pirtm.td
      pirtm-types-basic.mlir
    src/
      pirtm_types.cpp
    .github/workflows/
      pirtm-dialect.yml
```


### `pirtm.td`

- Four `TypeDef`s with:
    - Full doc blocks (what each type means in multiplicity terms).
    - `assemblyFormat` using `mod=` everywhere.
    - `genVerifyDecl = 1` for all types, so `pirtm_types.cpp` must implement:
        - `AtomicTensorType::verifyConstructionInvariants`
        - `CompositeTensorType::verifyConstructionInvariants`
        - `CertType::verifyConstructionInvariants`
        - `CertPairType::verifyConstructionInvariants`
- `Pirtm_SessionGraphOp` stub with:
    - `gain_matrix` as `OptionalAttr<DenseF64ArrayAttr>` so `#pirtm.unresolved_coupling` is legal at transpile time.
    - Verifier that:
        - Returns success immediately when `gain_matrix` is absent or sentinel.
        - Runs power iteration only when a concrete dense tensor is present.


### `pirtm_types.cpp`

- Pure arithmetic helpers:
    - `bool isPrime(int64_t)` — Miller–Rabin (deterministic for 64-bit).
    - `bool isSquarefree(int64_t)` — trial division up to √n checking μ(n) ≠ 0 (no repeated prime factors).
- Type verifiers:
    - `AtomicTensorType` → `isPrime(mod)`, nice error for 7921.
    - `CompositeTensorType` → `isSquarefree(mod)`, nice error for 49.
    - `CertType` → `isPrime(prime)`.
    - `CertPairType` → `isSquarefree(mod)` and consistent with constituent primes once `merge_cert` exists.


### `prime-to-mod-rename.md`

- File-scoped tables for the five affected files, split into:
    - “Rename” sites (`.prime` field, IR string literals).
    - “Do not rename” sites (`prime_index`, `_is_prime`, pass names).
- Shim protocol:
    - `PrimeChannel.prime` becomes a `@property` returning `self.mod` during transition.
    - Shim removed atomically at Day-14 merge.
- Two grep-based gates at bottom:
    - One for lingering `.prime` accesses outside the shim.
    - One for `prime=` in MLIR snippets.

This doc stays in Tooling as the **mechanical spec**. ADR-004 in PIRTM remains the **architectural spec**.

### `pirtm-types-basic.mlir`

- Exactly the four test cases you described, with `CHECK` and `expected-error` lines tied to:
    - “mod=7921 is not prime (7921 = 89 * 89)”
    - “mod=49 is not squarefree (49 = 7^2, μ(49) = 0)”

This forces the C++ verifier to emit full diagnostic context, not a generic failure.

## CI Wire-up

Minimal GitHub Action in Tooling:

```yaml
name: pirtm-dialect

on:
  workflow_call:
  push:
    paths:
      - 'pirtm-dialect/**'

jobs:
  test-pirtm-dialect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build pirtm dialect
        run: |
          cmake -S pirtm-dialect -B build
          cmake --build build
      - name: Run type-layer test
        run: |
          build/bin/mlir-opt pirtm-dialect/mlir/pirtm-types-basic.mlir \
            --verify-diagnostics
```

PIRTM’s repo can then call this workflow via `workflow_call` to keep dialect verification in one place.

## Precision Question

Now that the type layer and rename plan are living in Tooling, **do you want ADRs for dialect and tooling to be centralized there as well** (e.g., `Tooling/docs/adr/` as the single ADR home for all shared infra), or should PIRTM continue to own PIRTM-specific ADRs like ADR-004 while Tooling only carries implementation-level docs? That choice will decide whether the “source of truth” for future changes (e.g., adding new channel kinds or passes) is one ADR tree or two.
<span style="display:none">[^10_1][^10_10][^10_11][^10_12][^10_13][^10_14][^10_15][^10_16][^10_17][^10_18][^10_19][^10_2][^10_20][^10_21][^10_22][^10_23][^10_24][^10_3][^10_4][^10_5][^10_6][^10_7][^10_8][^10_9]</span>

<div align="center">⁂</div>

[^10_1]: https://github.com/mgeeky/ProtectMyTooling

[^10_2]: https://github.com/mskilab-org/multiplicity

[^10_3]: https://github.com/mims-harvard/ToolUniverse

[^10_4]: https://github.com/arcee-ai/mergekit

[^10_5]: https://github.com/alassek/multiplicity

[^10_6]: https://github.com/opinionated-digital-center/pyadr

[^10_7]: https://github.com/squidfunk/mkdocs-material/discussions/7852

[^10_8]: https://github.com/charliemarx/pmtools

[^10_9]: https://github.com/hmrc/platui-adr-spike

[^10_10]: https://github.com/multiply-org/multiply-core/wiki/Development-Process/_history

[^10_11]: https://github.com/siravan/symjit/

[^10_12]: https://github.com/adr/madr

[^10_13]: https://github.com/multiply-org/multiply-core/milestones?state=closed

[^10_14]: https://github.com/hiyouga/LLaMA-Factory

[^10_15]: https://github.com/joelparkerhenderson/architecture-decision-record

[^10_16]: https://github.com/socialfoundations/mono-multi

[^10_17]: https://github.com/tmgthb/Autonomous-Agents

[^10_18]: https://forum.mbse-capella.org/t/multiplicity-in-capella/5081

[^10_19]: https://github.com/vaskar-open-source-research/toolcomp

[^10_20]: https://www.fda.gov/science-research/data-mining/data-mining-fda-white-paper

[^10_21]: https://www.sciencedirect.com/science/article/pii/S1007570424003034

[^10_22]: https://mediatum.ub.tum.de/doc/1521926/448455.pdf

[^10_23]: https://ieeexplore.ieee.org/iel7/32/9775544/09201551.pdf

[^10_24]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12651923/


---

# lets create an ADR plan for these developments.

Create a small ADR *stack* that keeps ADR-004 as the normative spec, while moving Tooling-specific build/CI/layout decisions into separate “implementation ADRs” that reference ADR-004 rather than duplicating it.

## Central tension

We need to preserve **one** language/governance truth (ADR-004) while still allowing Tooling to evolve build plumbing, CI gates, and file layout without silently editing the spec.  The ADR plan below makes that separation explicit: PIRTM owns “what the system is,” Tooling owns “how we compile/test/enforce it.”

## Levers (owner, metric, horizon)

- Owner: Language Architect; Metric: ADR-004 remains the only place that defines semantics (kinds, passes, two-phase model, coupling schema, inspect/audit layers); Horizon: 7 days.
- Owner: Tooling Maintainer; Metric: Tooling ADRs only define build+test+repo layout and must include “Spec reference: ADR-004” header; Horizon: 7 days.
- Owner: CI/Infra; Metric: one CI workflow enforces the Day-0/Day-3 gates (TableGen compile + `mlir-opt --verify-diagnostics` on the basic types test); Horizon: 14 days.


## ADR plan (minimal set)

1) **Tooling-ADR-000: ADR process + directory layout**
Artifacts: `Tooling/docs/adr/README.md`, MADR template, naming/numbering rules, “spec vs implementation” rule.
2) **Tooling-ADR-001: PIRTM dialect type-layer gate (Day 0–3)**
Scope: `pirtm.td` TypeDefs + `SessionGraphOp` stub, `pirtm_types.cpp` verifier helpers, and `pirtm-types-basic.mlir` as the acceptance test; explicitly references ADR-004’s `mod=` and squarefree/prime constraints.
3) **Tooling-ADR-002: prime→mod migration + shim protocol (Day 0–14)**
Scope: the structured audit/migration doc, the temporary shim (`PrimeChannel.prime → property over .mod`), and the exact merge gate grep commands; explicitly references ADR-004’s atomic Day-14 rename requirement.
4) **Tooling-ADR-003: Linker inputs + coupling resolution gates (Day 14–16)**
Scope: `coupling.json` schema, the three-pass resolution pipeline, commitment-collision test, and where `pirtm_link.py` lives; references ADR-004’s link-time `session_graph` semantics.

## Artifacts to update first

- PIRTM: add a short note at the top of ADR-004: “Implementation ADRs live in Tooling; they may not redefine semantics.”
- Tooling: create `docs/adr/` + `Tooling-ADR-000` and land the three Day-0 artifacts alongside `Tooling-ADR-001` immediately.

Precision question: Should Tooling ADRs be allowed to introduce *new verifier diagnostics strings* (for the `.mlir` expected-error matching), or must those diagnostics be treated as spec-stable API and therefore require a PIRTM ADR update to change?
<span style="display:none">[^11_1][^11_10][^11_11][^11_12][^11_13][^11_14][^11_15][^11_16][^11_17][^11_18][^11_19][^11_2][^11_20][^11_21][^11_22][^11_23][^11_24][^11_25][^11_26][^11_27][^11_28][^11_3][^11_4][^11_5][^11_6][^11_7][^11_8][^11_9]</span>

<div align="center">⁂</div>

[^11_1]: https://github.com/mskilab-org/multiplicity

[^11_2]: https://github.com/mgeeky/ProtectMyTooling

[^11_3]: https://github.com/mims-harvard/ToolUniverse

[^11_4]: https://github.com/arcee-ai/mergekit

[^11_5]: https://github.com/alassek/multiplicity

[^11_6]: https://github.com/multiply-org/multiply-core/wiki/Development-Process/65066139a55263b2fdd9cbfa4e38388e7d7f4d71

[^11_7]: https://github.com/charliemarx/pmtools

[^11_8]: https://github.com/multiply-org/multiply-orchestration/blob/master/README.md

[^11_9]: https://github.com/rustdesk/rustdesk/wiki/FAQ

[^11_10]: https://github.com/alibaba/higress

[^11_11]: https://github.com/web-infra-dev/rslib

[^11_12]: https://github.com/TablePlus/TablePlus

[^11_13]: https://github.com/coreinfrastructure/best-practices-badge

[^11_14]: https://github.com/tylerjwatson/Multiplicity/blob/master/LICENSE

[^11_15]: https://github.com/golang/go/issues/32017

[^11_16]: https://github.com/socialfoundations/mono-multi

[^11_17]: https://github.com/volatilityfoundation

[^11_18]: https://github.com/orgs/volatilityfoundation/repositories

[^11_19]: https://github.com/realpython/codetiming

[^11_20]: https://github.com/JWatsonDaniels/multitarget-multiplicity

[^11_21]: https://github.com/volatilityfoundation/volatility/wiki/command-reference

[^11_22]: https://github.com/golemparts/rppal

[^11_23]: https://www.sciencedirect.com/science/article/pii/S2352711018301833

[^11_24]: https://github.com/stalwartlabs/mail-parser

[^11_25]: https://gftn.co/hubfs/multiplicity and convergence in the digital assets ecosystem_final.pdf

[^11_26]: https://github.com/chatmail/async-imap

[^11_27]: https://dl.acm.org/doi/10.1145/3677173

[^11_28]: https://www.repository.law.indiana.edu/cgi/viewcontent.cgi?article=11580\&context=ilj

