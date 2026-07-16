import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-slider-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="control-container">
      <label [for]="def.id">{{ def.label }} <span *ngIf="isRequired">*</span></label>
      <div class="slider-wrapper" style="display: flex; align-items: center; gap: 10px;">
        <input
          type="range"
          [id]="def.id"
          [attr.disabled]="def.disabled ? true : null"
          [min]="getMin()"
          [max]="getMax()"
          [step]="getStep()"
          [ngModel]="value"
          [ngModelOptions]="{standalone: true}"
          (ngModelChange)="onValueChange($event)"
          (blur)="touched = true"
          class="slider-input"
        />
        <span class="slider-value">{{ value !== undefined && value !== null ? value : '-' }}</span>
      </div>
      <div class="error-message" *ngIf="touched && !isValid">
        <div *ngFor="let err of errors">{{ err }}</div>
      </div>
    </div>
  `,
  styles: [`
    .control-container {
      margin-bottom: 1rem;
    }
    label {
      display: block;
      margin-bottom: 0.5rem;
      font-weight: bold;
    }
    .slider-input {
      flex: 1;
    }
    .slider-value {
      min-width: 3ch;
    }
    .error-message {
      color: red;
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SliderControlComponent extends BaseControl {

  getMin(): number | undefined {
    const minRule = this.def.validations?.find(r => r.type === 'min');
    return minRule ? Number(minRule.value) : undefined;
  }

  getMax(): number | undefined {
    const maxRule = this.def.validations?.find(r => r.type === 'max');
    return maxRule ? Number(maxRule.value) : undefined;
  }

  getStep(): number {
    return 1;
  }

  get isRequired(): boolean {
    return !!this.def.validations?.some(r => r.type === 'required');
  }

  // Override to handle numeric parsing from slider input
  override onValueChange(newValue: any): void {
    if (newValue === '' || newValue === null || newValue === undefined) {
      super.onValueChange(newValue);
    } else {
      super.onValueChange(Number(newValue));
    }
  }
}
