# PIRTM Mathematical Specification

This document is an implementation-oriented mathematical reference for `pirtm`.
The normative language definition is `docs/PIRTM_LANGUAGE_SPEC.md`.

## Contractive Recurrence

Implemented by `pirtm.recurrence.step`:

\[
X_{t+1} = \mathcal{P}(\Xi_t X_t + \Lambda_t T(X_t) + G_t)
\]

- `X_t \in \mathbb{R}^d`
- `\Xi_t, \Lambda_t \in \mathbb{R}^{d\times d}`
- `T: \mathbb{R}^d \to \mathbb{R}^d`
- `G_t \in \mathbb{R}^d`
- `\mathcal{P}` non-expansive projector

## Contraction Coefficient

\[
q_t = \|\Xi_t\|_2 + \|\Lambda_t\|_2\|T\|_{op}
\]

Safety target:

\[
q_t < 1 - \epsilon
\]

If violated, soft scaling projection enforces feasibility.

## ACE Certificate

`pirtm.certify.ace_certificate` computes

\[
q_{\max} = \max_t q_t,\quad target = 1-\min_t\epsilon_t,\quad margin = target - q_{\max}
\]

Certified iff `margin >= 0`.

Tail bound:

\[
\text{tail\_bound}=\begin{cases}
\frac{\text{tail\_norm}}{1-q_{\max}}, & q_{\max}<1 \\
\infty, & q_{\max}\ge 1
\end{cases}
\]

## ISS Bound

\[
\|X_t - X^*\| \le \frac{\|G\|_\infty}{1-q_{\max}}
\]

for stable `q_max < 1`.

## Weighted `\ell_1` Projection

`project_parameters_weighted_l1` solves

\[
\min_{x'} \|x'-x\|_2^2 \quad \text{s.t.}\quad \sum_i w_i|x'_i|\le B
\]

using threshold search + binary refinement.

## PETC Chain

A valid PETC chain is strictly increasing prime indices with bounded gaps:

\[
p_1 < p_2 < \dots < p_N,\quad p_i\in\mathbb{P},\quad p_{i+1}-p_i\le g_{max}
\]

Coverage over interval `[a,b]`:

\[
\rho = \frac{|\mathcal{C}\cap[a,b]|}{|\mathbb{P}\cap[a,b]|}
\]

## CSC Budget

\[
\|\Xi\| + \|\Lambda\|\|T\|_{op} \le 1-\epsilon
\]

Split with `\alpha`:

\[
\|\Xi\|_{\max}=\alpha(1-\epsilon),\quad
\|\Lambda\|_{\max}=\frac{(1-\alpha)(1-\epsilon)}{\|T\|_{op}}
\]
