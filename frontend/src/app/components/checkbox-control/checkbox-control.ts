import { Component, OnInit, OnDestroy, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-checkbox-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './checkbox-control.html',
  styleUrls: ['./checkbox-control.scss']
})
export class CheckboxControlComponent extends BaseControl implements OnInit, OnDestroy {
  override ngOnInit() {
    super.ngOnInit();
    if (this.value === undefined || this.value === null) {
      this.value = false;
    }
  }
  override ngOnDestroy() {
    super.ngOnDestroy();
  }
}
