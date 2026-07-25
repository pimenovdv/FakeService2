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

  get step(): number {
    const stepRule = this.def?.validations?.find(v => v.type === 'step');
    return stepRule?.value !== undefined ? Number(stepRule.value) : 1;
  }

  increment() {
    if (this.def.disabled) return;
    const currentValue = typeof this.value === 'number' ? this.value : 0;
    const step = this.step;
    const min = isFinite(this.min) ? this.min : 0;

    const stepCount = Math.floor((currentValue - min) / step);
    const snapDown = min + stepCount * step;

    // Calculate the next step value upwards
    let nextValue = snapDown + step;
    // Account for floating point inaccuracies
    if (Math.abs(nextValue - currentValue) < 1e-10) {
       nextValue += step;
    }

    // Convert back to original precision to avoid e.g. 0.30000000000000004
    nextValue = parseFloat(nextValue.toPrecision(12));

    if (nextValue <= this.max && nextValue !== currentValue) {
      this.onValueChange(nextValue);
    } else if (nextValue > this.max && this.max !== currentValue) {
      // If adding full step exceeds max, snap to max
      this.onValueChange(this.max);
    }
  }

  decrement() {
    if (this.def.disabled) return;
    const currentValue = typeof this.value === 'number' ? this.value : 0;
    const step = this.step;
    const min = isFinite(this.min) ? this.min : 0;

    const stepCount = Math.floor((currentValue - min) / step);
    let nextValue = min + stepCount * step;

    // Account for floating point inaccuracies - if we're already perfectly on the boundary, we need to go down one step
    if (Math.abs(nextValue - currentValue) < 1e-10) {
       nextValue -= step;
    }

    nextValue = parseFloat(nextValue.toPrecision(12));

    if (nextValue >= this.min && nextValue !== currentValue) {
      this.onValueChange(nextValue);
    } else if (nextValue < this.min && this.min !== currentValue) {
      // If subtracting full step goes below min, snap to min
      this.onValueChange(this.min);
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
    } else if (numValue > this.max) {
        numValue = this.max;
    } else {
        const step = this.step;
        const min = isFinite(this.min) ? this.min : 0;

        // Find closest valid step value
        const stepCount = Math.round((numValue - min) / step);
        numValue = min + stepCount * step;

        // Fix precision issues
        numValue = parseFloat(numValue.toPrecision(12));

        if (numValue > this.max) {
            numValue = this.max;
        }
        if (numValue < this.min) {
            numValue = this.min;
        }
    }

    this.onValueChange(numValue);
  }
}
