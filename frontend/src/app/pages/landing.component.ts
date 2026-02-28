import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="flex flex-col min-h-screen bg-[#050505] text-zinc-100 selection:bg-emerald-500/30">
      
      <!-- Hero Section -->
      <section class="container mx-auto px-4 pt-24 pb-16 md:pt-32 md:pb-24">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="space-y-8">
            <div class="inline-flex items-center rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-sm font-medium text-emerald-400">
              <span class="flex h-2 w-2 rounded-full bg-emerald-400 mr-2 animate-pulse"></span>
              v1.0.0 Stable Release
            </div>
            
            <h1 class="text-4xl font-extrabold tracking-tight lg:text-6xl text-white">
              Contractive Recurrence. <br/>
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">Certified Convergence.</span>
            </h1>
            
            <p class="text-xl text-zinc-400 max-w-[600px] leading-relaxed">
              PIRTM is a Python library for prime-indexed recursive tensor mathematics with provable stability bounds, adaptive governance, and ethical gating.
            </p>

            <div class="flex flex-col sm:flex-row gap-4">
              <div class="relative group">
                <div class="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-lg blur opacity-30 group-hover:opacity-100 transition duration-200"></div>
                <button class="relative flex items-center justify-center w-full sm:w-auto px-8 py-3 bg-black rounded-lg leading-none text-zinc-200 border border-zinc-800 hover:text-white transition-colors font-mono">
                  <span class="mr-2 text-emerald-500">$</span> pip install pirtm
                  <mat-icon class="ml-2 text-sm h-4 w-4 !text-[16px]">content_copy</mat-icon>
                </button>
              </div>
              <button class="px-8 py-3 rounded-lg bg-zinc-100 text-zinc-900 font-medium hover:bg-white transition-colors">
                Read the Docs
              </button>
            </div>

            <div class="flex flex-wrap gap-6 text-sm font-medium text-zinc-500 pt-4">
              <div class="flex items-center gap-2">
                <mat-icon class="text-emerald-500 !text-[20px]">check_circle</mat-icon>
                Contraction-guaranteed
              </div>
              <div class="flex items-center gap-2">
                <mat-icon class="text-emerald-500 !text-[20px]">verified_user</mat-icon>
                CSL-compliant
              </div>
              <div class="flex items-center gap-2">
                <mat-icon class="text-emerald-500 !text-[20px]">link</mat-icon>
                Audit-chained
              </div>
            </div>
          </div>

          <!-- Hero Visual: Recurrence Equation -->
          <div class="relative p-8 rounded-2xl bg-zinc-900/50 border border-white/10 backdrop-blur-sm">
            <div class="absolute top-0 right-0 -mr-4 -mt-4 w-24 h-24 bg-emerald-500/20 rounded-full blur-2xl"></div>
            <div class="absolute bottom-0 left-0 -ml-4 -mb-4 w-32 h-32 bg-cyan-500/20 rounded-full blur-2xl"></div>
            
            <div class="font-mono text-center space-y-8">
              <div class="text-sm text-zinc-500 uppercase tracking-widest">Recurrence Equation</div>
              <div class="text-2xl md:text-4xl font-bold text-white py-8 overflow-x-auto">
                X<sub class="text-zinc-500">t+1</sub> = P(Ξ<sub class="text-zinc-500">t</sub>X<sub class="text-zinc-500">t</sub> + Λ<sub class="text-zinc-500">t</sub>T(X<sub class="text-zinc-500">t</sub>) + G<sub class="text-zinc-500">t</sub>)
              </div>
              
              <div class="grid grid-cols-2 gap-4 text-left text-xs md:text-sm">
                <div class="p-3 rounded bg-black/40 border border-white/5">
                  <span class="text-emerald-400 font-bold">Ξ<sub>t</sub></span> : State Projection
                </div>
                <div class="p-3 rounded bg-black/40 border border-white/5">
                  <span class="text-cyan-400 font-bold">Λ<sub>t</sub></span> : Adaptive Operator
                </div>
                <div class="p-3 rounded bg-black/40 border border-white/5">
                  <span class="text-purple-400 font-bold">T(X)</span> : Tensor Transform
                </div>
                <div class="p-3 rounded bg-black/40 border border-white/5">
                  <span class="text-orange-400 font-bold">G<sub>t</sub></span> : Governance Gate
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- What Is PIRTM -->
      <section class="border-t border-white/5 bg-zinc-900/20">
        <div class="container mx-auto px-4 py-24">
          <div class="grid lg:grid-cols-2 gap-16">
            <div class="space-y-6">
              <h2 class="text-3xl font-bold text-white">Precision for High-Stakes Recursion</h2>
              <p class="text-zinc-400 leading-relaxed">
                PIRTM is not a general-purpose numerical solver. It is a specialized engine for prime-indexed recursive systems where stability is non-negotiable. Unlike standard solvers that drift, PIRTM enforces contractive dynamics at every step.
              </p>
              <p class="text-zinc-400 leading-relaxed">
                Designed for applied mathematicians and numerical engineers, it provides a rigorous framework for running recursive tensor operations with mathematically guaranteed convergence bounds.
              </p>
              <p class="text-zinc-400 leading-relaxed">
                Whether you are modeling quantum cognition or complex adaptive systems, PIRTM ensures your recurrence remains bounded, auditable, and ethically gated through the CSL framework.
              </p>
            </div>
            
            <div class="grid sm:grid-cols-2 gap-4">
              <div class="p-6 rounded-xl bg-black border border-white/10 hover:border-emerald-500/50 transition-colors group">
                <div class="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-4 group-hover:bg-emerald-500/20 transition-colors">
                  <mat-icon class="text-emerald-400">compress</mat-icon>
                </div>
                <h3 class="text-lg font-semibold text-white mb-2">Contractive Step</h3>
                <p class="text-sm text-zinc-500">Every step satisfies q < 1 - ε, ensuring strict convergence towards a stable fixed point.</p>
              </div>

              <div class="p-6 rounded-xl bg-black border border-white/10 hover:border-cyan-500/50 transition-colors group">
                <div class="h-10 w-10 rounded-lg bg-cyan-500/10 flex items-center justify-center mb-4 group-hover:bg-cyan-500/20 transition-colors">
                  <mat-icon class="text-cyan-400">tune</mat-icon>
                </div>
                <h3 class="text-lg font-semibold text-white mb-2">Adaptive Margin</h3>
                <p class="text-sm text-zinc-500">Epsilon auto-tunes via residual + contraction telemetry to maximize stability.</p>
              </div>

              <div class="p-6 rounded-xl bg-black border border-white/10 hover:border-purple-500/50 transition-colors group">
                <div class="h-10 w-10 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4 group-hover:bg-purple-500/20 transition-colors">
                  <mat-icon class="text-purple-400">verified</mat-icon>
                </div>
                <h3 class="text-lg font-semibold text-white mb-2">ACE Certification</h3>
                <p class="text-sm text-zinc-500">Post-run certificates with tail bounds and ISS guarantees for full auditability.</p>
              </div>

              <div class="p-6 rounded-xl bg-black border border-white/10 hover:border-orange-500/50 transition-colors group">
                <div class="h-10 w-10 rounded-lg bg-orange-500/10 flex items-center justify-center mb-4 group-hover:bg-orange-500/20 transition-colors">
                  <mat-icon class="text-orange-400">waves</mat-icon>
                </div>
                <h3 class="text-lg font-semibold text-white mb-2">Spectral Analysis</h3>
                <p class="text-sm text-zinc-500">Prime-indexed eigenvalue decomposition and phase coherence tracking.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- How It Works -->
      <section class="container mx-auto px-4 py-24">
        <h2 class="text-3xl font-bold text-white text-center mb-16">The PIRTM Pipeline</h2>
        <div class="grid md:grid-cols-3 gap-8 relative">
          <!-- Connector Line (Desktop) -->
          <div class="hidden md:block absolute top-12 left-[16%] right-[16%] h-0.5 bg-gradient-to-r from-zinc-800 via-emerald-900 to-zinc-800 -z-10"></div>

          <div class="relative flex flex-col items-center text-center">
            <div class="h-24 w-24 rounded-full bg-black border-2 border-zinc-800 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(16,185,129,0.1)] z-10">
              <span class="font-mono text-2xl font-bold text-emerald-500">01</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">Define Operators</h3>
            <p class="text-zinc-400 text-sm max-w-xs">Supply T, P, and parameter sequences Ξt, Λt, Gt to configure the system dynamics.</p>
          </div>

          <div class="relative flex flex-col items-center text-center">
            <div class="h-24 w-24 rounded-full bg-black border-2 border-zinc-800 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(6,182,212,0.1)] z-10">
              <span class="font-mono text-2xl font-bold text-cyan-500">02</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">Run Recurrence</h3>
            <p class="text-zinc-400 text-sm max-w-xs">pirtm.run() auto-projects parameters to maintain contraction and records telemetry per step.</p>
          </div>

          <div class="relative flex flex-col items-center text-center">
            <div class="h-24 w-24 rounded-full bg-black border-2 border-zinc-800 flex items-center justify-center mb-6 shadow-[0_0_30px_rgba(168,85,247,0.1)] z-10">
              <span class="font-mono text-2xl font-bold text-purple-500">03</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-3">Certify Results</h3>
            <p class="text-zinc-400 text-sm max-w-xs">ace_certificate() produces a Certificate with margin, tail bound, and convergence status.</p>
          </div>
        </div>
      </section>

      <!-- Code Example -->
      <section class="bg-zinc-900/30 border-y border-white/5 py-24">
        <div class="container mx-auto px-4">
          <div class="max-w-4xl mx-auto">
            <div class="flex items-center justify-between mb-8">
              <h2 class="text-2xl font-bold text-white">Developer Interface</h2>
              <div class="text-sm text-zinc-500">Every step is telemetered. Every run is certifiable.</div>
            </div>

            <div class="rounded-xl overflow-hidden border border-white/10 bg-[#0A0A0A] shadow-2xl">
              <div class="flex border-b border-white/10 bg-white/5">
                <button 
                  (click)="activeTab = 'quickstart'" 
                  [class.text-emerald-400]="activeTab === 'quickstart'"
                  [class.bg-white/5]="activeTab === 'quickstart'"
                  class="px-6 py-3 text-sm font-mono font-medium text-zinc-400 hover:text-white transition-colors border-r border-white/5">
                  quickstart.py
                </button>
                <button 
                  (click)="activeTab = 'adaptive'" 
                  [class.text-cyan-400]="activeTab === 'adaptive'"
                  [class.bg-white/5]="activeTab === 'adaptive'"
                  class="px-6 py-3 text-sm font-mono font-medium text-zinc-400 hover:text-white transition-colors border-r border-white/5">
                  adaptive.py
                </button>
                <button 
                  (click)="activeTab = 'spectral'" 
                  [class.text-purple-400]="activeTab === 'spectral'"
                  [class.bg-white/5]="activeTab === 'spectral'"
                  class="px-6 py-3 text-sm font-mono font-medium text-zinc-400 hover:text-white transition-colors">
                  spectral.py
                </button>
              </div>

              <div class="p-6 overflow-x-auto">
                <pre class="font-mono text-sm leading-relaxed" *ngIf="activeTab === 'quickstart'"><code class="text-zinc-300"><span class="text-purple-400">import</span> numpy <span class="text-purple-400">as</span> np
<span class="text-purple-400">from</span> pirtm <span class="text-purple-400">import</span> step, ace_certificate

<span class="text-zinc-500"># Initialize State and Parameters</span>
X = np.zeros(4)
Xi = 0.3 * np.eye(4)
Lam = 0.2 * np.eye(4)
T = <span class="text-purple-400">lambda</span> x: np.tanh(x)
G = np.random.randn(4) * 0.01
P = <span class="text-purple-400">lambda</span> x: np.clip(x, -1, 1)

<span class="text-zinc-500"># Run a single step with epsilon constraint</span>
X_next, info = step(X, Xi, Lam, T, G, P, epsilon=0.05)

<span class="text-zinc-500"># Generate Audit Certificate</span>
cert = ace_certificate(info, tail_norm=0.01)

print(<span class="text-emerald-300">f"q={{ '{' }}info.q:.4f{{ '}' }}, certified={{ '{' }}cert.certified{{ '}' }}, margin={{ '{' }}cert.margin:.4f{{ '}' }}"</span>)</code></pre>

                <pre class="font-mono text-sm leading-relaxed" *ngIf="activeTab === 'adaptive'"><code class="text-zinc-300"><span class="text-purple-400">from</span> pirtm <span class="text-purple-400">import</span> AdaptiveMargin, Monitor

<span class="text-zinc-500"># Initialize Adaptive Margin Controller</span>
am = AdaptiveMargin(initial_epsilon=0.1, decay=0.99)
monitor = Monitor()

<span class="text-purple-400">for</span> t <span class="text-purple-400">in</span> range(100):
    <span class="text-zinc-500"># Auto-tune epsilon based on residual history</span>
    eps = am.update(monitor.history)
    
    X_next, info = step(X, Xi, Lam, T, G, P, epsilon=eps)
    monitor.record(t, info)
    
    <span class="text-purple-400">if</span> not info.contractive:
        am.intervene()
        break</code></pre>

                <pre class="font-mono text-sm leading-relaxed" *ngIf="activeTab === 'spectral'"><code class="text-zinc-300"><span class="text-purple-400">from</span> pirtm.spectral <span class="text-purple-400">import</span> decompose, coherence

<span class="text-zinc-500"># Perform Prime-Indexed Spectral Decomposition</span>
eigenvals, eigenvecs = decompose(operator=T, index_basis=<span class="text-emerald-300">'prime'</span>)

<span class="text-zinc-500"># Check Phase Coherence</span>
phase_lock = coherence(eigenvecs, reference_state=X)

print(<span class="text-emerald-300">f"Spectral Entropy: {{ '{' }}np.sum(np.abs(eigenvals)):.4f{{ '}' }}"</span>)
print(<span class="text-emerald-300">f"Phase Lock: {{ '{' }}phase_lock:.2f{{ '}' }}"</span>)</code></pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Roadmap -->
      <section class="container mx-auto px-4 py-24">
        <h2 class="text-3xl font-bold text-white mb-12">Tier Roadmap</h2>
        <div class="max-w-3xl mx-auto space-y-8 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-zinc-700 before:to-transparent">
          
          <div class="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            <div class="flex items-center justify-center w-10 h-10 rounded-full border border-emerald-500 bg-emerald-500/20 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.3)] shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
              <mat-icon class="text-sm">check</mat-icon>
            </div>
            <div class="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm">
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-white">Tier 1: Installable Package</span>
                <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Complete</span>
              </div>
              <p class="text-sm text-zinc-400">Core library structure and pip distribution.</p>
            </div>
          </div>

          <div class="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            <div class="flex items-center justify-center w-10 h-10 rounded-full border border-emerald-500 bg-emerald-500/20 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.3)] shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
              <mat-icon class="text-sm">check</mat-icon>
            </div>
            <div class="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm">
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-white">Tier 2: Complete API Surface</span>
                <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Complete</span>
              </div>
              <p class="text-sm text-zinc-400">Full implementation of step, run, and certify functions.</p>
            </div>
          </div>

          <div class="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
            <div class="flex items-center justify-center w-10 h-10 rounded-full border border-cyan-500 bg-cyan-500/20 text-cyan-400 shadow-[0_0_10px_rgba(6,182,212,0.3)] shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
              <mat-icon class="text-sm">sync</mat-icon>
            </div>
            <div class="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm">
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-white">Tier 6: Emission Gating</span>
                <span class="text-xs px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">In Progress</span>
              </div>
              <p class="text-sm text-zinc-400">Telemetry + Q-ARI integration for safety.</p>
            </div>
          </div>

          <div class="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
            <div class="flex items-center justify-center w-10 h-10 rounded-full border border-zinc-700 bg-zinc-800 text-zinc-500 shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
              <mat-icon class="text-sm">schedule</mat-icon>
            </div>
            <div class="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm">
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold text-white">Tier 8: Ξ-Certification</span>
                <span class="text-xs px-2 py-0.5 rounded bg-zinc-700/50 text-zinc-400 border border-zinc-700">Planned</span>
              </div>
              <p class="text-sm text-zinc-400">Full pipeline for constitutional certification.</p>
            </div>
          </div>

        </div>
      </section>

      <!-- Ecosystem Map -->
      <section class="container mx-auto px-4 py-24 border-t border-white/5">
        <h2 class="text-3xl font-bold text-white text-center mb-16">The Multiplicity Ecosystem</h2>
        
        <div class="relative max-w-4xl mx-auto h-[400px] bg-zinc-900/30 rounded-2xl border border-white/5 p-8 flex items-center justify-center overflow-hidden">
          <!-- Background Grid -->
          <div class="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>
          
          <svg class="w-full h-full" viewBox="0 0 800 400" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Edges -->
            <path d="M200 200 L 400 100" stroke="#34d399" stroke-width="2" stroke-dasharray="5 5" class="animate-pulse opacity-50" />
            <path d="M400 100 L 600 200" stroke="#34d399" stroke-width="2" />
            <path d="M600 200 L 400 300" stroke="#a855f7" stroke-width="2" />
            <path d="M400 300 L 200 200" stroke="#06b6d4" stroke-width="2" />
            
            <!-- Nodes -->
            <!-- PIRTM -->
            <g transform="translate(200, 200)">
              <circle r="40" fill="#050505" stroke="#10b981" stroke-width="2" />
              <text x="0" y="5" text-anchor="middle" fill="white" font-family="monospace" font-weight="bold">PIRTM</text>
              <text x="0" y="60" text-anchor="middle" fill="#10b981" font-size="12">Recurrence</text>
            </g>

            <!-- Lambda-Proof -->
            <g transform="translate(600, 200)">
              <circle r="40" fill="#050505" stroke="#a855f7" stroke-width="2" />
              <text x="0" y="5" text-anchor="middle" fill="white" font-family="monospace" font-weight="bold">Λ-Proof</text>
              <text x="0" y="60" text-anchor="middle" fill="#a855f7" font-size="12">Governance</text>
            </g>

            <!-- DRMM -->
            <g transform="translate(400, 300)">
              <circle r="40" fill="#050505" stroke="#06b6d4" stroke-width="2" />
              <text x="0" y="5" text-anchor="middle" fill="white" font-family="monospace" font-weight="bold">DRMM</text>
              <text x="0" y="60" text-anchor="middle" fill="#06b6d4" font-size="12">Feedback</text>
            </g>

            <!-- Constitution -->
            <g transform="translate(400, 100)">
              <rect x="-60" y="-20" width="120" height="40" rx="20" fill="#050505" stroke="#fbbf24" stroke-width="2" />
              <text x="0" y="5" text-anchor="middle" fill="#fbbf24" font-family="monospace" font-weight="bold">Ξ-Constitution</text>
            </g>
          </svg>
        </div>
      </section>

      <!-- CTA -->
      <section class="border-t border-white/10 bg-gradient-to-b from-zinc-900 to-black py-24 text-center">
        <div class="container mx-auto px-4">
          <h2 class="text-3xl font-bold text-white mb-6">Start building with PIRTM</h2>
          <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
            <div class="px-6 py-3 rounded-lg bg-zinc-900 border border-zinc-800 font-mono text-zinc-300">
              pip install pirtm
            </div>
            <a routerLink="/docs" class="px-6 py-3 rounded-lg bg-white text-black font-medium hover:bg-zinc-200 transition-colors">
              View Documentation
            </a>
          </div>
        </div>
      </section>

    </div>
  `
})
export class LandingComponent {
  activeTab = 'quickstart';
}
