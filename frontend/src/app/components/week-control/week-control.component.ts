import { Component, ChangeDetectionStrategy, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-week-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './week-control.component.html',
  styleUrls: ['./week-control.component.css'],
  providers: [
    {
      provide: BaseControl,
      useExisting: forwardRef(() => WeekControlComponent)
    }
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class WeekControlComponent extends BaseControl {
  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }

  onModelChange(newValue: any): void {
    this.onValueChange(newValue);
  }
}
