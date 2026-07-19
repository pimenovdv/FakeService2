import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-button-group-control',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './button-group-control.component.html',
  styleUrls: ['./button-group-control.component.scss']
})
export class ButtonGroupControlComponent extends BaseControl {
  constructor() {
    super();
  }

  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }

  selectOption(val: any) {
    if (this.def?.disabled) {
      return;
    }
    this.value = val;
    this.onValueChange(val);
    this.validate();
  }
}
