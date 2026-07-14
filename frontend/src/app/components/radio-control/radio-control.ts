import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-radio-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './radio-control.html',
  styleUrls: ['./radio-control.scss']
})
export class RadioControlComponent extends BaseControl implements OnInit, OnDestroy {
  override ngOnInit() {
    super.ngOnInit();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }
}
