import { Component, ChangeDetectionStrategy, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { AutofocusDirective } from '../../directives/autofocus.directive';

@Component({
  selector: 'app-search-control',
  standalone: true,
  imports: [CommonModule, FormsModule, AutofocusDirective],
  templateUrl: './search-control.component.html',
  styleUrls: ['./search-control.component.css'],
  providers: [
    {
      provide: BaseControl,
      useExisting: forwardRef(() => SearchControlComponent)
    }
  ],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class SearchControlComponent extends BaseControl {
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
