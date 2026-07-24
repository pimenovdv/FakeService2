import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';
import { MaskDirective } from '../../directives/mask.directive';

@Component({
  selector: 'app-phone-control',
  standalone: true,
  imports: [CommonModule, FormsModule, MaskDirective],
  templateUrl: './phone-control.html',
  styleUrls: ['./phone-control.scss']
})
export class PhoneControlComponent extends BaseControl implements OnInit, OnDestroy {
  get isRequired(): boolean {
    return !!this.def?.validations?.some(v => v.type === 'required');
  }

  override ngOnInit() {
    super.ngOnInit();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }
}
