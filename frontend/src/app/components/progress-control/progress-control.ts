import { Component, ChangeDetectionStrategy, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-progress-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="control-container">
      <label [for]="def.id">{{ def.label }} <span *ngIf="isRequired">*</span></label>
      <div class="progress-wrapper">
        <progress
          #progressEl
          [id]="def.id"
          [attr.disabled]="def.disabled ? true : null"
          [max]="getMax()"
          [value]="getNumericValue()"
          (click)="onClick($event)"
          class="progress-input"
          [class.disabled]="def.disabled === true"
        ></progress>
        <span class="progress-value">{{ getNumericValue() }}%</span>
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
    .progress-wrapper {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .progress-input {
      flex: 1;
      cursor: pointer;
    }
    .progress-input.disabled {
      cursor: not-allowed;
    }
    .progress-value {
      min-width: 4ch;
      text-align: right;
    }
    .error-message {
      color: red;
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ProgressControlComponent extends BaseControl {
  @ViewChild('progressEl') progressEl!: ElementRef<HTMLProgressElement>;

  getMax(): number {
    return 100;
  }

  getNumericValue(): number {
    if (this.value === undefined || this.value === null || this.value === '') {
      return 0;
    }
    return Number(this.value);
  }

  get isRequired(): boolean {
    return !!this.def.validations?.some(r => r.type === 'required');
  }

  onClick(event: MouseEvent) {
    if (this.def.disabled === true) {
      return;
    }
    this.touched = true;

    if (this.progressEl) {
      const el = this.progressEl.nativeElement;
      const rect = el.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const width = rect.width;

      let percentage = (x / width) * this.getMax();
      percentage = Math.max(0, Math.min(percentage, this.getMax()));
      const rounded = Math.round(percentage);

      this.onValueChange(rounded);
      this.validate();
    }
  }
}
