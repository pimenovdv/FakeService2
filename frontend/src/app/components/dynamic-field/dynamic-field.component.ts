import { Component, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ComponentDef } from '../../models/screen.model';
import { TextInputComponent } from '../text-input/text-input';
import { ComboboxControlComponent } from '../combobox-control/combobox-control';
import { StateService } from '../../services/state';

@Component({
  selector: 'app-dynamic-field',
  standalone: true,
  imports: [CommonModule, TextInputComponent, ComboboxControlComponent],
  templateUrl: './dynamic-field.component.html'
})
export class DynamicFieldComponent {
  @Input() componentDef!: ComponentDef;

  public stateService = inject(StateService);

  get show(): boolean {
    if (this.componentDef.hidden) return false;
    return this.stateService.evaluateCondition(this.componentDef.showIf);
  }

  get isDisabled(): boolean {
    if (this.componentDef.disabled) return true;
    if (this.componentDef.disableIf) {
      return this.stateService.evaluateCondition(this.componentDef.disableIf);
    }
    return false;
  }
}
