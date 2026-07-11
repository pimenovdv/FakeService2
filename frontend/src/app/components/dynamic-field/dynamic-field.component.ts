import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComponentDef } from '../../models/screen.model';
import { TextInputComponent } from '../text-input/text-input';
import { ComboboxControlComponent } from '../combobox-control/combobox-control';

@Component({
  selector: 'app-dynamic-field',
  standalone: true,
  imports: [CommonModule, TextInputComponent, ComboboxControlComponent],
  templateUrl: './dynamic-field.component.html'
})
export class DynamicFieldComponent {
  @Input() componentDef!: ComponentDef;
}
