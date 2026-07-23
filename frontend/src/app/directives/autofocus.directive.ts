import { Directive, ElementRef, Input, AfterViewInit } from '@angular/core';

@Directive({
  selector: '[appAutofocus]',
  standalone: true
})
export class AutofocusDirective implements AfterViewInit {
  @Input('appAutofocus') autofocusEnabled: boolean | undefined = false;

  constructor(private el: ElementRef) {}

  ngAfterViewInit() {
    if (this.autofocusEnabled) {
      setTimeout(() => {
        this.el.nativeElement.focus();
      }, 0);
    }
  }
}
