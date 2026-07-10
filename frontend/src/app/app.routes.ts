import { Routes } from '@angular/router';
import { Player } from './components/player/player';

export const routes: Routes = [
  { path: ':service_id/1', component: Player }
];
