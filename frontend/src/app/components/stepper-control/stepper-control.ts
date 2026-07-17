import { Component, ChangeDetectionStrategy, ChangeDetectorRef, Optional, Inject, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { NG_VALUE_ACCESSOR } from '@angular/forms';

@Component({
  selector: 'app-stepper-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './stepper-control.html',
  styleUrls: ['./stepper-control.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => StepperControlComponent),
      multi: true,
    }
  ]
})
export class StepperControlComponent extends BaseControl {
  constructor(private cdr: ChangeDetectorRef) {
    super();
  }

  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }

  get min(): number {
    const minRule = this.def?.validations?.find(v => v.type === 'min');
    return minRule?.value !== undefined ? minRule.value : -Infinity;
  }

  get max(): number {
    const maxRule = this.def?.validations?.find(v => v.type === 'max');
    return maxRule?.value !== undefined ? maxRule.value : Infinity;
  }

  increment() {
    if (this.def.disabled) return;
    const currentValue = typeof this.value === 'number' ? this.value : 0;
    if (currentValue < this.max) {
      this.onValueChange(currentValue + 1);
    }
  }

  decrement() {
    if (this.def.disabled) return;
    const currentValue = typeof this.value === 'number' ? this.value : 0;
    if (currentValue > this.min) {
      this.onValueChange(currentValue - 1);
    }
  }

  onInputBlur() {
    this.touched = true;
    let numValue = Number(this.value);

    if (isNaN(numValue)) {
      numValue = 0;
    }

    if (numValue < this.min) {
        numValue = this.min;
    }
    if (numValue > this.max) {
        numValue = this.max;
    }

    this.onValueChange(numValue);
  }
}
