import { Component, ChangeDetectionStrategy, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, NG_VALUE_ACCESSOR } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-datetime-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './datetime-control.component.html',
  styleUrls: ['./datetime-control.component.css'],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => DatetimeControlComponent),
      multi: true
    }
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DatetimeControlComponent extends BaseControl {
  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }
}
