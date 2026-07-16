import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-color-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="control-container">
      <label [for]="def.id">{{ def.label }} <span *ngIf="isRequired">*</span></label>
      <div style="display: flex; align-items: center; gap: 10px;">
        <input
          type="color"
          [id]="def.id"
          [attr.disabled]="def.disabled ? true : null"
          [ngModel]="value"
          [ngModelOptions]="{standalone: true}"
          (ngModelChange)="onValueChange($event)"
          (blur)="touched = true"
          class="color-input"
        />
        <span class="color-value">{{ value ? value : '-' }}</span>
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
    .color-input {
      width: 40px;
      height: 40px;
      padding: 0;
      border: 1px solid #ccc;
      border-radius: 4px;
      cursor: pointer;
    }
    .color-input:disabled {
      cursor: not-allowed;
      opacity: 0.6;
    }
    .color-value {
      font-family: monospace;
    }
    .error-message {
      color: red;
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ColorControlComponent extends BaseControl {
  get isRequired(): boolean {
    return !!this.def.validations?.some(r => r.type === 'required');
  }
}
