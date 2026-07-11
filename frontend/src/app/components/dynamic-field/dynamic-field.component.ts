import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComponentDef } from '../../models/screen.model';
import { TextInputComponent } from '../text-input/text-input';

@Component({
  selector: 'app-dynamic-field',
  standalone: true,
  imports: [CommonModule, TextInputComponent],
  templateUrl: './dynamic-field.component.html'
})
export class DynamicFieldComponent {
  @Input() componentDef!: ComponentDef;
}
