import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComponentDef } from '../../models/screen.model';

@Component({
  selector: 'app-divider-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './divider-control.html'
})
export class DividerControlComponent {
  @Input() def!: ComponentDef;
}
