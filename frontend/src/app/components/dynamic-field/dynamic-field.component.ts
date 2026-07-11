import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComponentDef } from '../../models/screen.model';

@Component({
  selector: 'app-dynamic-field',
  imports: [CommonModule],
  templateUrl: './dynamic-field.component.html'
})
export class DynamicFieldComponent {
  @Input() componentDef!: ComponentDef;
}
