import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-playground',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="min-h-screen bg-[#050505] pt-20 pb-12">
      <div class="container mx-auto px-4 h-[calc(100vh-8rem)]">
        <div class="flex items-center justify-between mb-6">
          <h1 class="text-2xl font-bold text-white flex items-center gap-3">
            <mat-icon class="text-emerald-500">terminal</mat-icon>
            Live Recurrence Runner
          </h1>
          <div class="flex gap-3">
            <button class="px-4 py-2 rounded bg-zinc-800 text-zinc-300 text-sm hover:bg-zinc-700 transition-colors">
              Load Template
            </button>
            <button class="px-4 py-2 rounded bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors flex items-center gap-2">
              <mat-icon class="text-sm h-4 w-4 !text-[16px]">play_arrow</mat-icon>
              Run
            </button>
          </div>
        </div>

        <div class="grid lg:grid-cols-2 gap-6 h-full">
          <!-- Editor Pane -->
          <div class="rounded-xl border border-zinc-800 bg-[#0A0A0A] flex flex-col overflow-hidden">
            <div class="flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-zinc-900/50">
              <span class="text-xs font-mono text-zinc-400">main.py</span>
              <span class="text-xs text-emerald-500 flex items-center gap-1">
                <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                Pyodide Ready
              </span>
            </div>
            <div class="flex-1 p-4 font-mono text-sm text-zinc-300 overflow-auto">
              <pre><code>import numpy as np
from pirtm import step, certify_state

# Initialize operators
X = np.zeros(4)
Xi = 0.3 * np.eye(4)   # State projection
Lam = 0.2 * np.eye(4)  # Aggregation

print("Starting recurrence...")
for i in range(10):
    X, info = step(X, Xi, Lam)
    cert = certify_state(X, epsilon=0.05)
    print(f"Step {{ '{' }}i{{ '}' }}: ||X||={{ '{' }}info['norm_X_next']:.4f{{ '}' }}, valid={{ '{' }}cert.is_valid(){{ '}' }}")</code></pre>
            </div>
          </div>

          <!-- Output Pane -->
          <div class="rounded-xl border border-zinc-800 bg-[#0A0A0A] flex flex-col overflow-hidden">
            <div class="flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-zinc-900/50">
              <span class="text-xs font-mono text-zinc-400">Output</span>
              <button class="text-xs text-zinc-500 hover:text-white">Clear</button>
            </div>
            <div class="flex-1 p-4 font-mono text-sm text-zinc-400 overflow-auto">
              <div class="text-zinc-500 italic mb-2"># Output will appear here...</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class PlaygroundComponent {}
