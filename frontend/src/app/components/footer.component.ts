import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  standalone: true,
  template: `
    <footer class="border-t border-white/10 bg-black py-6 md:py-0">
      <div class="container mx-auto flex flex-col items-center justify-between gap-4 md:h-24 md:flex-row px-4">
        <div class="flex flex-col items-center gap-4 px-8 md:flex-row md:gap-2 md:px-0">
          <p class="text-center text-sm leading-loose text-zinc-400 md:text-left">
            Built by <span class="font-medium underline underline-offset-4">Multiplicity Foundation</span>.
            The source code is available on <a href="#" class="font-medium underline underline-offset-4">GitHub</a>.
          </p>
        </div>
        <p class="text-center text-sm text-zinc-400 md:text-left">
          MIT License
        </p>
      </div>
    </footer>
  `
})
export class FooterComponent {}
