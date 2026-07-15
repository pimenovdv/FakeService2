import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-number-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './number-control.html',
  styleUrls: ['./number-control.scss']
})
export class NumberControlComponent extends BaseControl implements OnInit, OnDestroy {
  override ngOnInit() {
    super.ngOnInit();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }
}
