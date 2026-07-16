import { Component, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-toggle-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="control-container">
      <label class="toggle-label" [for]="def.id">
        <div class="toggle-switch">
          <input
            type="checkbox"
            [id]="def.id"
            [attr.disabled]="def.disabled ? true : null"
            [ngModel]="value"
            [ngModelOptions]="{standalone: true}"
            (ngModelChange)="onValueChange($event)"
            (blur)="touched = true"
            class="toggle-input"
          />
          <span class="slider round"></span>
        </div>
        <span class="label-text">{{ def.label }} <span *ngIf="isRequired">*</span></span>
      </label>
      <div class="error-message" *ngIf="touched && !isValid">
        <div *ngFor="let err of errors">{{ err }}</div>
      </div>
    </div>
  `,
  styles: [`
    .control-container {
      margin-bottom: 1rem;
    }
    .toggle-label {
      display: flex;
      align-items: center;
      cursor: pointer;
    }
    .toggle-label.disabled {
      cursor: not-allowed;
      opacity: 0.6;
    }
    .label-text {
      margin-left: 10px;
      font-weight: bold;
    }
    /* The switch - the box around the slider */
    .toggle-switch {
      position: relative;
      display: inline-block;
      width: 50px;
      height: 24px;
    }

    /* Hide default HTML checkbox */
    .toggle-switch input {
      opacity: 0;
      width: 0;
      height: 0;
    }

    /* The slider */
    .slider {
      position: absolute;
      cursor: pointer;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background-color: #ccc;
      transition: .4s;
    }

    .slider:before {
      position: absolute;
      content: "";
      height: 16px;
      width: 16px;
      left: 4px;
      bottom: 4px;
      background-color: white;
      transition: .4s;
    }

    input:checked + .slider {
      background-color: #2196F3;
    }

    input:focus + .slider {
      box-shadow: 0 0 1px #2196F3;
    }

    input:checked + .slider:before {
      transform: translateX(26px);
    }

    input:disabled + .slider {
      background-color: #e0e0e0;
      cursor: not-allowed;
    }
    input:disabled + .slider:before {
      background-color: #bdbdbd;
    }

    /* Rounded sliders */
    .slider.round {
      border-radius: 24px;
    }

    .slider.round:before {
      border-radius: 50%;
    }

    .error-message {
      color: red;
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ToggleControlComponent extends BaseControl {
  get isRequired(): boolean {
    return !!this.def.validations?.some(r => r.type === 'required');
  }
}
