import { Component, ChangeDetectionStrategy, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-month-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './month-control.component.html',
  styleUrls: ['./month-control.component.css'],
  providers: [
    {
      provide: BaseControl,
      useExisting: forwardRef(() => MonthControlComponent)
    }
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MonthControlComponent extends BaseControl {
  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }

  onModelChange(newValue: any): void {
    this.onValueChange(newValue);
  }
}
