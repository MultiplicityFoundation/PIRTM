import { Routes } from '@angular/router';
import { LandingComponent } from './pages/landing.component';
import { DocsComponent } from './pages/docs.component';
import { PlaygroundComponent } from './pages/playground.component';
import { CertificationComponent } from './pages/certification.component';
import { EcosystemComponent } from './pages/ecosystem.component';
import { ResearchComponent } from './pages/research.component';

export const routes: Routes = [
  { path: '', component: LandingComponent },
  { path: 'docs', component: DocsComponent },
  { path: 'playground', component: PlaygroundComponent },
  { path: 'certification', component: CertificationComponent },
  { path: 'ecosystem', component: EcosystemComponent },
  { path: 'research', component: ResearchComponent },
  { path: '**', redirectTo: '' }
];
