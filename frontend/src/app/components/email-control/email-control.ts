import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-email-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './email-control.html',
  styleUrls: ['./email-control.scss']
})
export class EmailControlComponent extends BaseControl implements OnInit, OnDestroy {
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
