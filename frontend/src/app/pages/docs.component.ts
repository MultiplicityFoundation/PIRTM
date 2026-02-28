import { Component } from '@angular/core';

@Component({
  selector: 'app-docs',
  standalone: true,
  template: `
    <div class="container mx-auto px-4 py-12 text-white">
      <h1 class="text-3xl font-bold mb-4">Documentation</h1>
      <p class="text-zinc-400">API reference and tutorials coming soon.</p>
    </div>
  `
})
export class DocsComponent {}
