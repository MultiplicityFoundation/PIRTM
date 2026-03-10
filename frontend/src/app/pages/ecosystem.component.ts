import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-ecosystem',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="min-h-screen bg-[#050505] pt-20 pb-12 text-zinc-100">
      <div class="container mx-auto px-4 py-12 max-w-4xl">
        <h1 class="text-3xl font-bold mb-2 text-white">Ecosystem</h1>
        <p class="text-zinc-400 mb-10">
          Relationship to Λ-Proof, DRMM, Ξ-Constitution, and the broader Multiplicity platform.
        </p>

        <div class="grid sm:grid-cols-2 gap-6 mb-12">
          <div class="p-6 rounded-xl border border-emerald-500/30 bg-emerald-500/5">
            <div class="flex items-center gap-3 mb-3">
              <span class="font-mono text-xl font-bold text-emerald-400">PIRTM</span>
              <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400">Core</span>
            </div>
            <p class="text-sm text-zinc-400">
              Contractive recurrence runtime. Provides the mathematical foundation:
              verified step(), certify_state(), and the MLIR dialect with compile-time guarantees.
            </p>
          </div>

          <div class="p-6 rounded-xl border border-purple-500/30 bg-purple-500/5">
            <div class="flex items-center gap-3 mb-3">
              <span class="font-mono text-xl font-bold text-purple-400">Λ-Proof</span>
            </div>
            <p class="text-sm text-zinc-400">
              Governance layer. Integrates with PIRTM's ACE certificates to produce
              auditable proof chains for session attribution.
            </p>
          </div>

          <div class="p-6 rounded-xl border border-cyan-500/30 bg-cyan-500/5">
            <div class="flex items-center gap-3 mb-3">
              <span class="font-mono text-xl font-bold text-cyan-400">DRMM</span>
            </div>
            <p class="text-sm text-zinc-400">
              Dynamic Recursive Margin Monitor. Reads PIRTM telemetry to provide
              real-time feedback on contraction margin and stability trends.
            </p>
          </div>

          <div class="p-6 rounded-xl border border-yellow-500/30 bg-yellow-500/5">
            <div class="flex items-center gap-3 mb-3">
              <span class="font-mono text-xl font-bold text-yellow-400">Ξ-Constitution</span>
            </div>
            <p class="text-sm text-zinc-400">
              Constitutional layer. Wraps PIRTM sessions with ethical gating and CSL
              (Contractive Session Logic) compliance verification.
            </p>
          </div>
        </div>

        <!-- GAP Integration -->
        <section>
          <h2 class="text-xl font-semibold text-white mb-4">GAP Integration</h2>
          <div class="p-5 rounded-xl border border-zinc-800 bg-black">
            <div class="flex items-center gap-3 mb-3">
              <mat-icon class="text-zinc-400">calculate</mat-icon>
              <span class="font-semibold text-white">Computer Algebra System</span>
            </div>
            <p class="text-sm text-zinc-400">
              <code class="text-emerald-300">pirtm.integrations.q2_gap</code> provides a bridge to the GAP computer
              algebra system for formal verification of algebraic properties. Used for
              prime-index uniqueness proofs and group-theoretic spectral bounds.
            </p>
          </div>
        </section>
      </div>
    </div>
  `
})
export class EcosystemComponent {}
