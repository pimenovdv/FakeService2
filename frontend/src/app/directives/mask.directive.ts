import { Directive, ElementRef, HostListener, Input, Optional } from '@angular/core';
import { NgControl } from '@angular/forms';

@Directive({
  selector: '[appMask]',
  standalone: true
})
export class MaskDirective {
  @Input('appMask') mask?: string;

  constructor(
    private el: ElementRef<HTMLInputElement>,
    @Optional() private control: NgControl
  ) {}

  @HostListener('input', ['$event'])
  onInput(event: Event) {
    if (!this.mask) return;

    let input = this.el.nativeElement.value;

    // Strip all non-alphanumeric characters for processing
    const cleanInput = input.replace(/[^a-zA-Z0-9]/g, '');
    let formatted = '';
    let maskIndex = 0;
    let inputIndex = 0;

    // Apply the mask
    while (maskIndex < this.mask.length && inputIndex < cleanInput.length) {
      const maskChar = this.mask[maskIndex];
      const inputChar = cleanInput[inputIndex];

      if (maskChar === '0') {
        // Number expected
        if (/[0-9]/.test(inputChar)) {
          formatted += inputChar;
          inputIndex++;
        } else {
            // Invalid character for this position, skip to next input character
            inputIndex++;
            continue; // Keep maskIndex same to try again
        }
      } else if (maskChar === 'A') {
         // Alphabet expected
         if (/[a-zA-Z]/.test(inputChar)) {
             formatted += inputChar;
             inputIndex++;
         } else {
             inputIndex++;
             continue;
         }
      } else if (maskChar === '*') {
         // Alphanumeric expected
         formatted += inputChar;
         inputIndex++;
      } else {
        // Static mask character
        formatted += maskChar;
      }
      maskIndex++;
    }

    // Set the formatted value back
    this.el.nativeElement.value = formatted;

    // Update the control if it exists
    if (this.control && this.control.control) {
        this.control.control.setValue(formatted);
    }
  }
}