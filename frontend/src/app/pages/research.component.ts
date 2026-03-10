import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-research',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="min-h-screen bg-[#050505] pt-20 pb-12 text-zinc-100">
      <div class="container mx-auto px-4 py-12 max-w-4xl">
        <h1 class="text-3xl font-bold mb-2 text-white">Research</h1>
        <p class="text-zinc-400 mb-10">
          Theoretical foundations, spectral analysis, and open problems in contractive recurrence.
        </p>

        <div class="space-y-8">
          <!-- Recurrence Equation -->
          <div class="p-6 rounded-xl border border-zinc-800 bg-black">
            <div class="flex items-center gap-3 mb-4">
              <mat-icon class="text-emerald-400">functions</mat-icon>
              <h2 class="text-lg font-semibold text-white">Recurrence Equation</h2>
            </div>
            <p class="font-mono text-center text-xl text-white py-4">
              X<sub class="text-zinc-500">t+1</sub> = P(Ξ<sub class="text-zinc-500">t</sub>X<sub class="text-zinc-500">t</sub>
              + Λ<sub class="text-zinc-500">t</sub>T(X<sub class="text-zinc-500">t</sub>) + G<sub class="text-zinc-500">t</sub>)
            </p>
            <p class="text-sm text-zinc-400">
              Contractivity is guaranteed when
              <span class="font-mono text-emerald-300">||Ξ|| + ||Λ||·||T'|| &lt; 1 − ε</span>.
              This condition is verified at transpile-time via MLIR and at link-time via the spectral-small-gain test.
            </p>
          </div>

          <!-- Spectral Analysis -->
          <div class="p-6 rounded-xl border border-zinc-800 bg-black">
            <div class="flex items-center gap-3 mb-4">
              <mat-icon class="text-cyan-400">waves</mat-icon>
              <h2 class="text-lg font-semibold text-white">Spectral Analysis</h2>
            </div>
            <p class="text-sm text-zinc-400 mb-3">
              PIRTM uses AAA (Adaptive Antoulas-Anderson) rational approximation for complex resonance detection
              and a Prime-Cayley Laplacian for operator fingerprinting.
            </p>
            <div class="font-mono text-xs text-zinc-500 space-y-1">
              <div>pirtm.spectral.aaa       — AAA rational approximation</div>
              <div>pirtm.spectral.laplacian  — Prime-Cayley Laplacian</div>
              <div>pirtm.spectral.fingerprint — 5-point spectral shape test</div>
              <div>pirtm.spectral.continuation — Analytic continuation</div>
            </div>
          </div>

          <!-- Prime Indexing -->
          <div class="p-6 rounded-xl border border-zinc-800 bg-black">
            <div class="flex items-center gap-3 mb-4">
              <mat-icon class="text-purple-400">tag</mat-icon>
              <h2 class="text-lg font-semibold text-white">Prime Indexing</h2>
            </div>
            <p class="text-sm text-zinc-400">
              Every PIRTM module is assigned a unique <span class="font-mono text-purple-300">prime_index</span>.
              The MLIR dialect enforces Miller-Rabin primality at construction time —
              composite <span class="font-mono">mod=</span> values are rejected with a factorization error.
              Session graphs require squarefree composite indices; atomic types require primes.
            </p>
          </div>
        </div>
      </div>
    </div>
  `
})
export class ResearchComponent {}
