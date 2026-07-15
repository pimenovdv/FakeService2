import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-datepicker-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './datepicker-control.html',
  styleUrls: ['./datepicker-control.scss']
})
export class DatepickerControlComponent extends BaseControl implements OnInit, OnDestroy {
  override ngOnInit() {
    super.ngOnInit();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }

}
