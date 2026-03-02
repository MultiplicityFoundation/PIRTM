# PIRTM Language Specification

**Document ID:** PIRTM-SPEC-1.0  
**Status:** Normative Draft  
**Date:** 2026-03-01  
**Authority:** Multiplicity Foundation

---

## Preamble

This document defines the **PIRTM Language** — the canonical formal system for
Prime-Indexed Recursive Tensor Mathematics. It specifies the grammar, type
system, canonical forms, and evaluation invariants of PIRTM as a computation
language, independent of any implementation.

The language has four distinguishing properties that, in combination, constitute
its novel contribution:

1. **Contractive typing** — every well-formed expression carries a proof that
   the recurrence contracts by at least $\epsilon > 0$.
2. **Prime-indexed ordering** — every step carries a prime number as an
   audit-chain position, enforcing a total, gap-bounded ordering over all
   computation events.
3. **Emission predication** — output is not produced by execution; it is
   produced only when a language-level gate predicate is satisfied.
4. **Witness commitment** — every emitted output binds (state hash × prime
   index × contraction certificate) into a single commitment that can be
   verified without re-executing the computation.

This specification is the authoritative source. Conforming implementations
must derive their behavior from these definitions, not from any reference
implementation.

---

## §1 Notation and Primitives

### §1.1 Base Types

The PIRTM type universe $U$ is defined over the following primitives:

| Symbol | Domain | Name |
|---|---|---|
| $d$ | $\mathbb{N}_{+}$ | Dimension |
| $\epsilon$ | $\mathbb{R}_{+}$ | Safety margin |
| $q$ | $[0, 1)$ | Contraction coefficient |
| $X$ | $\mathbb{R}^d$ | State vector |
| $\Xi$ | $\mathbb{R}^{d\times d}$ | Gain matrix (linear part) |
| $\Lambda$ | $\mathbb{R}^{d\times d}$ | Gain matrix (nonlinear part) |
| $T$ | $\mathbb{R}^d \to \mathbb{R}^d$ | Nonlinear operator |
| $G$ | $\mathbb{R}^d$ | Driving input |
| $P$ | $\mathbb{R}^d \to \mathbb{R}^d$ | Projector |
| $p$ | $\mathbb{P}$ | Prime index |
| $h$ | $\{0,1\}^{256}$ | State hash (SHA-256 or Poseidon-compat) |

### §1.2 Operator Norms

For any matrix $M \in \mathbb{R}^{d\times d}$, $\|M\|$ denotes the spectral norm (largest
singular value). For any operator $T: \mathbb{R}^d \to \mathbb{R}^d$, $\|T\|_{op}$ denotes the
operator norm:

$$
\|T\|_{op} = \sup \left\{ \frac{\|T(x)\|}{\|x\|} : x \neq 0 \right\}
$$

A projector $P$ is **non-expansive** iff for all $x, y \in \mathbb{R}^d$:

$$
\|P(x) - P(y)\| \le \|x - y\|
$$

This is a necessary (but not sufficient) condition for $P$ to be admitted as
a projector in a well-formed PIRTM expression. The identity operator $\lambda x.x$
satisfies this condition trivially.

### §1.3 The Prime Set

$\mathbb{P}$ denotes the set of prime numbers in increasing order: $\{2,3,5,7,11,\dots\}$.
The **prime successor** of $p \in \mathbb{P}$ is written $p^{+}$, the smallest prime greater
than $p$. The **prime gap** at $p$ is $gap(p) = p^{+} - p$.

---

## §2 Expression Grammar

A **PIRTM expression** $E$ is defined by the following grammar (EBNF):

```ebnf
E ::=
    STEP(X, Ξ, Λ, T, G, P, ε)         (* primitive recurrence step *)
  | INDEX(E, p)                         (* prime-index annotation   *)
  | SEQ(E, E)                           (* sequential composition   *)
  | GATE(E, φ)                          (* emission gate            *)
  | WITNESS(E, h, scheme)               (* witness commitment       *)
  | BUDGET(E, α)                        (* CSC budget allocation    *)
```

Each production is defined in the sections below. The grammar is closed: no
other productions are admitted.

---

## §3 Type System

### §3.1 Expression Types

Every PIRTM expression $E$ has a type annotation $\tau$ of the form:

$$
\tau = (d, q, \epsilon, p?)
$$

where:

- $d$ is the dimension of the state space,
- $q$ is the contraction coefficient (upper bound over all steps in $E$),
- $\epsilon$ is the safety margin (lower bound over all steps in $E$),
- $p?$ is the prime index ($\bot$ if unindexed).

### §3.2 Typing Judgment

The judgment $\Gamma \vdash E : \tau$ is read "under context $\Gamma$, expression $E$ has type $\tau$."

**STEP typing rule:**

$$
\frac{}{\Gamma \vdash STEP(X,\Xi,\Lambda,T,G,P,\epsilon) : (d,\|\Xi\| + \|\Lambda\|\cdot\|T\|_{op},\epsilon,\bot)}\;(T\text{-}STEP)
$$

**INDEX typing rule:**

$$
\frac{\Gamma \vdash E : (d,q,\epsilon,\bot)\quad p\in\mathbb{P}}{\Gamma \vdash INDEX(E,p) : (d,q,\epsilon,p)}\;(T\text{-}INDEX)
$$

**SEQ typing rule:**

$$
\frac{\Gamma \vdash E_1 : (d,q_1,\epsilon_1,p_1)\quad \Gamma \vdash E_2 : (d,q_2,\epsilon_2,p_2)\quad p_1,p_2\in\mathbb{P}\quad p_1<p_2}{\Gamma \vdash SEQ(E_1,E_2):(d,\max(q_1,q_2),\min(\epsilon_1,\epsilon_2),p_2)}\;(T\text{-}SEQ)
$$

**GATE typing rule:**

$$
\frac{\Gamma \vdash E:(d,q,\epsilon,p)\quad \varphi:(d,q,\epsilon,p)\to\mathbb{B}}{\Gamma \vdash GATE(E,\varphi):(d,q,\epsilon,p)}\;(T\text{-}GATE)
$$

**WITNESS typing rule:**

$$
\frac{\Gamma \vdash E:(d,q,\epsilon,p)\quad p\neq\bot\quad scheme\in\{sha256,poseidon\_compat,dual\}}{\Gamma \vdash WITNESS(E,h,scheme):(d,q,\epsilon,p)}\;(T\text{-}WITNESS)
$$

**BUDGET typing rule:**

$$
\frac{\Gamma \vdash E:(d,q,\epsilon,p)\quad \alpha\in(0,1)}{\Gamma \vdash BUDGET(E,\alpha):(d,q,\epsilon,p)}\;(T\text{-}BUDGET)
$$

The split induced is:

$$
\|\Xi\|_{max}=\alpha\cdot(1-\epsilon),\qquad
\|\Lambda\|_{max}=\frac{(1-\alpha)(1-\epsilon)}{\|T\|_{op}}
$$

### §3.3 The Certified Type

An expression $E$ is **certified** iff its type $\tau=(d,q,\epsilon,p)$ satisfies:

$$
q < 1-\epsilon
$$

This is the **L0 invariant** of the PIRTM language.

---

## §4 Contraction Coefficient (Canonical Form)

The contraction coefficient for a STEP expression is defined canonically as:

$$
q(\Xi,\Lambda,T)=\|\Xi\|_2 + \|\Lambda\|_2\cdot\|T\|_{op}
$$

The safety condition $q < 1-\epsilon$ ensures strict contraction on $\mathbb{R}^d$.

---

## §5 Certificate Types

### §5.1 Minimal Certificate

The minimal contraction certificate is:

$$
	ext{Certificate}_{\min}=\{certified\in\mathbb{B}\}
$$

### §5.2 Standard Certificate

The standard implementation certificate is:

$$
	ext{Certificate}=\{certified,\ margin,\ tail\_bound,\ details\}
$$

where `details` carries implementation diagnostics (for example `max_q`,
`target`, and step metadata).

### §5.3 ACE Certificate

The **Absolute Contraction Evidence (ACE) certificate** for an expression $E$
is the record:

$$
ACE=\{q_{max},\ target,\ margin,\ certified,\ tail\_bound\}
$$

with formation:

$$
q_{max}=\max_t q_t,\quad target=1-\min_t\epsilon_t,\quad margin=target-q_{max},\quad certified=(margin\ge 0)
$$

$$
tail\_bound=\begin{cases}
\|G\|_{\infty}/(1-q_{max}), & certified\\
\infty, & \text{otherwise}
\end{cases}
$$

### §5.4 API Mapping

| Python API | Returns | Use Case |
| :-- | :-- | :-- |
| `contraction_certificate(info)` | `Certificate` | Standard contraction validation |
| `ace_certificate(info)` | `AceCertificate` | ACE diagnostics |
| `iss_bound(info, disturbance_norm)` | `float` | ISS bound |

---

## §6 ISS Bound

For certified expressions with fixed input $G$:

$$
\|X_t-X^*\| \le \frac{\|G\|_\infty}{1-q_{max}}
$$

---

## §7 PETC Chain (Prime-Indexed Event Ordering)

### §7.1 Chain Definition

A **PETC chain** $C$ is a finite sequence of prime indices:

$$
C = \langle p_1,p_2,\dots,p_N \rangle
$$

A PETC chain is valid iff:

1. Primality: $\forall i,\ p_i\in\mathbb{P}$
2. Strict monotonicity: $p_1 < p_2 < \dots < p_N$
3. Gap bound: $\forall i<N,\ p_{i+1}-p_i\le g_{max}$

### §7.2 Coverage

$$
\rho(C,[a,b]) = \frac{|\{p_i\in C: a\le p_i\le b\}|}{|\{p\in\mathbb{P}: a\le p\le b\}|}
$$

### §7.3 Ordering Invariant

Distinct prime-indexed events are globally ordered by prime index without
runtime coordination.

---

## §8 Emission Gate

### §8.1 Gate Predicate

An emission gate is a total predicate:

$$
\varphi : (StepInfo \times ACE) \to \{EMIT, SUPPRESS, HOLD\}
$$

### §8.2 Gate Policies

| Policy | Predicate | Semantics |
| :-- | :-- | :-- |
| PASS_THROUGH | $\varphi=\lambda\_.EMIT$ | All outputs emitted |
| CERTIFIED_ONLY | Emit iff `ACE.certified` | Emit only if ACE holds |
| CSL_GATED | `CSL(s) ∧ ACE.certified` | Two-stage: CSL then ACE |
| SILENT | $\varphi=\lambda\_.SUPPRESS$ | No output emitted |

### §8.3 CSL Evaluation

Canonical form:

$$
CSL(X,T,X') = (\|X' - T(X)\| \le \delta_{csl}) \land (\|X'\| \le B_{csl})
$$

---

## §9 Witness Language

### §9.1 Witness Record

A witness record includes at minimum:

- `primeIndex`, `stepIndex`
- `prevStateHash`, `newStateHash`, `stateHash`
- `merkleRoot`
- `certificate`
- `hashScheme ∈ {sha256, poseidon_compat, dual}`

Dual-hash mode additionally carries SHA-256 + Poseidon-specific hash fields.

### §9.2 Witness Formation Rule

A witness record $W$ is well-formed iff:

1. $W.primeIndex\in\mathbb{P}$
2. $W.certificate.certified=true$
3. $W.newStateHash=hash(W.prevStateHash\parallel Encode(X_{t+1}),W.hashScheme)$
4. $W.merkleRoot=MerkleRoot(\{W_i.newStateHash\})$ over prior steps

### §9.3 Audit Chain

An audit chain $A=\langle W_1,\dots,W_N\rangle$ is valid iff:

1. Every $W_i$ is well-formed
2. Prime indices are strictly increasing
3. Hash chain linkage holds: $W_{i+1}.prevStateHash = W_i.newStateHash$

---

## §10 Canonicalization

### §10.1 Normal Form

A PIRTM expression is in normal form iff:

1. Every STEP is prime-indexed
2. Any STEP with $q\ge 1-\epsilon$ is projected to satisfy L0
3. Sequence ordering is strictly prime-monotone
4. Gate policies are well-typed and canonical
5. Witness records are well-formed when enabled

### §10.2 Canonicalization Algorithm

Apply to completion:

1. **Index** bare STEP with next prime
2. **Project** gains if $q\ge 1-\epsilon$
3. **Order** to enforce strict prime monotonicity
4. **Gate** with default policy when absent
5. **Witness** on EMIT when witnessing is enabled

---

## §11 L0 Invariants

| # | Invariant | Formal Statement |
| :-- | :-- | :-- |
| L0.1 | Contractive typing | $\forall E$: $q(E) < 1 - \epsilon(E)$ |
| L0.2 | Prime uniqueness | $\forall E_1,E_2$ same session: $p(E_1) \ne p(E_2)$ |
| L0.3 | Prime monotonicity | $\forall SEQ(E_1,E_2)$: $p(E_1) < p(E_2)$ |
| L0.4 | Certified emission | $\forall E$ with `EMIT`: `ACE(E).certified = true` |
| L0.5 | Hash chain integrity | Consecutive witnesses chain on hashes |
| L0.6 | Witness linkage | Witness prime index equals expression prime index |

Violation of any L0 invariant renders the expression ill-typed.

---

## §12 Conformance Classes

| Class | Requirements |
| :-- | :-- |
| **Core** | §2 grammar, §3 type system, §5 certificate types, L0.1 |
| **Ordered** | Core + §7 PETC chain, L0.2, L0.3 |
| **Gated** | Ordered + §8 emission gate, L0.4 |
| **Witnessed** | Gated + §9 witness language, L0.5, L0.6 |
| **Full** | All sections |

The reference implementation in this repository targets **Full** conformance.

---

## §13 Normative References

- Banach Fixed-Point Theorem (metric space contraction)
- NIST FIPS 180-4 (SHA-256)
- Poseidon hash function (ZK-compatible)
- Merkle tree construction (RFC 6962 §2.1)
- Input-to-State Stability (Sontag, 1989)

---

*End of PIRTM Language Specification v1.0.0*
