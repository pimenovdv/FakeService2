import { Routes } from '@angular/router';
import { Player } from './components/player/player';
import { DraftsComponent } from './components/drafts/drafts';

export const routes: Routes = [
  { path: 'drafts', component: DraftsComponent },
  { path: ':service_id/1', component: Player }
];
