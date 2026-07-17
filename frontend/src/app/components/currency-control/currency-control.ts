import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-currency-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './currency-control.html',
  styleUrls: ['./currency-control.scss']
})
export class CurrencyControlComponent extends BaseControl implements OnInit, OnDestroy {
  override ngOnInit() {
    super.ngOnInit();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }
}
