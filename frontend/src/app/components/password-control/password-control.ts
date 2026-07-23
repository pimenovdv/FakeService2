import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-password-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './password-control.html',
  styleUrls: ['./password-control.scss']
})
export class PasswordControlComponent extends BaseControl implements OnInit, OnDestroy {
  showPassword = false;

  override ngOnInit() {
    super.ngOnInit();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  clearValue() {
    this.onValueChange('');
  }
}
