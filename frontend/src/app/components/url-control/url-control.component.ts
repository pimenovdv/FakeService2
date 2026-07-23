import { Component, ChangeDetectionStrategy, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-url-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './url-control.component.html',
  styleUrls: ['./url-control.component.css'],
  providers: [
    {
      provide: BaseControl,
      useExisting: forwardRef(() => UrlControlComponent)
    }
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UrlControlComponent extends BaseControl {
  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }

  onModelChange(newValue: any): void {
    this.onValueChange(newValue);
  }

  clearValue() {
    this.onValueChange('');
  }
}
