import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BaseControl } from '../base-control/base-control';

@Component({
  selector: 'app-captcha-control',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './captcha-control.html',
  styleUrls: ['./captcha-control.scss']
})
export class CaptchaControlComponent extends BaseControl implements OnInit, OnDestroy {
  captchaText: string = '';

  override ngOnInit() {
    this.generateCaptcha();
    super.ngOnInit();
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
  }

  generateCaptcha() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    this.captchaText = '';
    for (let i = 0; i < 6; i++) {
      this.captchaText += chars.charAt(Math.floor(Math.random() * chars.length));
    }
  }

  refreshCaptcha(event: Event) {
    event.preventDefault();
    this.generateCaptcha();
    this.onValueChange(''); // Reset value when refreshed
  }

  override validate() {
    super.validate(); // Run basic validations (like required)

    if (this.def.disabled || this.def.hidden) {
      return;
    }

    // Only validate captcha match if they've typed something, or if they haven't and it's not required,
    // wait, if it's not required, they still have to match it if they type something.
    // If it is required, base validation handles "This field is required".
    // We'll add our specific message.
    if (this.value && this.value !== this.captchaText) {
      this.errors.push('CAPTCHA does not match');
    }
  }
}
