import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-docs',
  standalone: true,
  imports: [CommonModule, RouterLink, MatIconModule],
  template: `
    <div class="min-h-screen bg-[#050505] pt-20 pb-12 text-zinc-100">
      <div class="container mx-auto px-4 py-12 max-w-4xl">
        <h1 class="text-3xl font-bold mb-2 text-white">Documentation</h1>
        <p class="text-zinc-400 mb-10">API reference for the PIRTM contractive recurrence runtime.</p>

        <!-- Installation -->
        <section class="mb-12">
          <h2 class="text-xl font-semibold text-white mb-4">Installation</h2>
          <div class="rounded-xl border border-zinc-800 bg-[#0A0A0A] p-4 font-mono text-sm text-zinc-300">
            <span class="text-emerald-500">$</span> pip install pirtm
          </div>
          <p class="text-zinc-500 text-sm mt-2">Requires Python ≥ 3.10 and NumPy ≥ 1.24.</p>
        </section>

        <!-- Core API -->
        <section class="mb-12">
          <h2 class="text-xl font-semibold text-white mb-6">Core API</h2>
          <div class="space-y-4">
            <div class="p-5 rounded-xl border border-zinc-800 bg-black">
              <div class="font-mono text-emerald-300 mb-2">pirtm.step(X_t, Xi_t, Lambda_t, G_t=None, T_func=None, backend=None)</div>
              <p class="text-sm text-zinc-400">
                Execute one contractive recurrence step: X_{{t+1}} = P(Ξ X_t + Λ T(X_t) + G_t).
                Returns <code class="text-cyan-300">(X_next, metadata)</code> where metadata contains per-step norms and backend info.
              </p>
            </div>
            <div class="p-5 rounded-xl border border-zinc-800 bg-black">
              <div class="font-mono text-emerald-300 mb-2">pirtm.certify_state(X, epsilon=0.05, confidence=0.9999, trace_id='pirtm_cert', backend=None)</div>
              <p class="text-sm text-zinc-400">
                Create a <code class="text-cyan-300">ContractivityCertificate</code> for the current state.
                Verifies the L0 invariant: ||X|| &lt; 1 − ε.
              </p>
            </div>
            <div class="p-5 rounded-xl border border-zinc-800 bg-black">
              <div class="font-mono text-emerald-300 mb-2">pirtm.verify_trajectory(trajectory, epsilon=0.05, backend=None)</div>
              <p class="text-sm text-zinc-400">
                Validate an entire trajectory satisfies contractivity at every step.
                Returns <code class="text-cyan-300">&#123; all_valid, violations, max_margin, total_steps &#125;</code>.
              </p>
            </div>
            <div class="p-5 rounded-xl border border-zinc-800 bg-black">
              <div class="font-mono text-emerald-300 mb-2">pirtm.compute_spectral_radius(A, backend=None)</div>
              <p class="text-sm text-zinc-400">
                Compute the spectral radius r(A) = max|eigenvalue| of a square matrix.
                Used to verify gain-contraction: r(Λ) &lt; 1 − ε.
              </p>
            </div>
          </div>
        </section>

        <!-- ADRs -->
        <section>
          <h2 class="text-xl font-semibold text-white mb-4">Architecture Decision Records</h2>
          <div class="grid sm:grid-cols-2 gap-3">
            <div class="p-4 rounded-lg border border-zinc-800 hover:border-emerald-500/40 transition-colors">
              <div class="text-sm font-mono text-emerald-400 mb-1">ADR-004</div>
              <div class="text-sm text-zinc-300">Contractivity Semantics</div>
            </div>
            <div class="p-4 rounded-lg border border-zinc-800 hover:border-emerald-500/40 transition-colors">
              <div class="text-sm font-mono text-emerald-400 mb-1">ADR-006</div>
              <div class="text-sm text-zinc-300">Backend Abstraction Protocol</div>
            </div>
            <div class="p-4 rounded-lg border border-zinc-800 hover:border-emerald-500/40 transition-colors">
              <div class="text-sm font-mono text-emerald-400 mb-1">ADR-007</div>
              <div class="text-sm text-zinc-300">MLIR Lowering &amp; Round-Trip</div>
            </div>
            <div class="p-4 rounded-lg border border-zinc-800 hover:border-emerald-500/40 transition-colors">
              <div class="text-sm font-mono text-emerald-400 mb-1">ADR-009</div>
              <div class="text-sm text-zinc-300">LLVM Compilation Pipeline</div>
            </div>
          </div>
        </section>
      </div>
    </div>
  `
})
export class DocsComponent {}
