import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-certification',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="min-h-screen bg-[#050505] pt-20 pb-12 text-zinc-100">
      <div class="container mx-auto px-4 py-12 max-w-4xl">
        <h1 class="text-3xl font-bold mb-2 text-white">Certification</h1>
        <p class="text-zinc-400 mb-10">
          ACE (Asymmetric Convergence Envelope) certificates, CSL verdicts, and contractivity proofs.
        </p>

        <!-- Certificate Model -->
        <section class="mb-12">
          <h2 class="text-xl font-semibold text-white mb-4">ContractivityCertificate</h2>
          <div class="rounded-xl border border-zinc-800 bg-[#0A0A0A] p-6 font-mono text-sm">
            <div class="text-zinc-500 mb-4"># from pirtm import certify_state</div>
            <div class="space-y-2 text-zinc-300">
              <div><span class="text-cyan-400">cert.epsilon</span>        <span class="text-zinc-500">→</span> contraction margin ε</div>
              <div><span class="text-cyan-400">cert.state_norm</span>     <span class="text-zinc-500">→</span> ||X_t||₂</div>
              <div><span class="text-cyan-400">cert.spectral_radius</span><span class="text-zinc-500">→</span> r(operator)</div>
              <div><span class="text-cyan-400">cert.is_valid()</span>     <span class="text-zinc-500">→</span> state_norm &lt; 1 − ε</div>
              <div><span class="text-cyan-400">cert.contraction_margin()</span> <span class="text-zinc-500">→</span> (1 − ε) − ||X_t||₂</div>
              <div><span class="text-cyan-400">cert.trace_id</span>       <span class="text-zinc-500">→</span> unique audit identifier</div>
            </div>
          </div>
        </section>

        <!-- L0 Invariant -->
        <section class="mb-12">
          <h2 class="text-xl font-semibold text-white mb-4">L0 Invariant</h2>
          <div class="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-6">
            <p class="font-mono text-emerald-300 text-lg text-center py-4">||X_t|| &lt; 1 − ε</p>
            <p class="text-zinc-400 text-sm text-center">
              Must hold at every step. Verified at transpile-time (contractivity-check)
              and at link-time (spectral-small-gain test).
            </p>
          </div>
        </section>

        <!-- Verification Phases -->
        <section>
          <h2 class="text-xl font-semibold text-white mb-4">Verification Phases</h2>
          <div class="grid md:grid-cols-2 gap-4">
            <div class="p-5 rounded-xl border border-zinc-800 bg-black">
              <div class="flex items-center gap-3 mb-3">
                <mat-icon class="text-emerald-400">verified</mat-icon>
                <span class="font-semibold text-white">Transpile-Time</span>
              </div>
              <p class="text-sm text-zinc-400">
                Per-module contractivity-check when <code class="text-emerald-300">.pirtm.bc</code> bytecode is produced.
                Fails fast if ||Ξ|| + ||Λ||·||T'|| ≥ 1 − ε.
              </p>
            </div>
            <div class="p-5 rounded-xl border border-zinc-800 bg-black">
              <div class="flex items-center gap-3 mb-3">
                <mat-icon class="text-cyan-400">link</mat-icon>
                <span class="font-semibold text-white">Link-Time</span>
              </div>
              <p class="text-sm text-zinc-400">
                Network-wide spectral-small-gain test when modules are linked into a session graph.
                Validates the coupled system remains contractive.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  `
})
export class CertificationComponent {}
