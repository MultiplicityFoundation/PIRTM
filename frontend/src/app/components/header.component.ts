import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
  template: `
    <header class="sticky top-0 z-50 w-full border-b border-white/10 bg-black/50 backdrop-blur-xl supports-[backdrop-filter]:bg-black/20">
      <div class="container mx-auto flex h-14 items-center px-4">
        <div class="mr-4 flex">
          <a routerLink="/" class="mr-6 flex items-center space-x-2">
            <span class="font-mono text-xl font-bold tracking-tighter text-white">
              <span class="text-emerald-400">PIRTM</span>
            </span>
          </a>
          <nav class="hidden md:flex items-center space-x-6 text-sm font-medium text-zinc-400">
            <a routerLink="/docs" routerLinkActive="text-white" class="transition-colors hover:text-white">Docs</a>
            <a routerLink="/playground" routerLinkActive="text-white" class="transition-colors hover:text-white">Playground</a>
            <a routerLink="/certification" routerLinkActive="text-white" class="transition-colors hover:text-white">Certification</a>
            <a routerLink="/ecosystem" routerLinkActive="text-white" class="transition-colors hover:text-white">Ecosystem</a>
            <a routerLink="/research" routerLinkActive="text-white" class="transition-colors hover:text-white">Research</a>
          </nav>
        </div>
        <div class="flex flex-1 items-center justify-end space-x-4">
          <nav class="flex items-center space-x-2">
            <a href="https://github.com" target="_blank" rel="noreferrer" class="text-zinc-400 hover:text-white">
              <span class="sr-only">GitHub</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-github"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
            </a>
            <a routerLink="/" class="inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-700 disabled:pointer-events-none disabled:opacity-50 border border-zinc-800 bg-zinc-950 shadow-sm hover:bg-zinc-800 hover:text-zinc-50 h-9 px-4 py-2 text-zinc-100">
              Install
            </a>
          </nav>
        </div>
      </div>
    </header>
  `
})
export class HeaderComponent {}
