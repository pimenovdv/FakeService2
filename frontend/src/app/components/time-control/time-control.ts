import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-time-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="control-container">
      <label [for]="def.id">{{ def.label }} <span *ngIf="isRequired">*</span></label>
      <input
        type="time"
        [id]="def.id"
        [attr.disabled]="def.disabled ? true : null"
        [ngModel]="value"
        [ngModelOptions]="{standalone: true}"
        (ngModelChange)="onValueChange($event)"
        (blur)="touched = true"
        class="time-input"
      />
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
    .time-input {
      width: 100%;
      padding: 0.5rem;
      border: 1px solid #ccc;
      border-radius: 4px;
      font-family: inherit;
    }
    .time-input:disabled {
      background-color: #f0f0f0;
      cursor: not-allowed;
    }
    .error-message {
      color: red;
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class TimeControlComponent extends BaseControl {
  get isRequired(): boolean {
    return !!this.def.validations?.some(r => r.type === 'required');
  }
}
