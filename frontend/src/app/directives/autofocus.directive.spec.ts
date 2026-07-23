import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AutofocusDirective } from './autofocus.directive';

@Component({
  template: `<input type="text" [appAutofocus]="isAutofocus" />`,
  standalone: true,
  imports: [AutofocusDirective]
})
class TestComponent {
  isAutofocus = true;
}

describe('AutofocusDirective', () => {
  let fixture: ComponentFixture<TestComponent>;
  let component: TestComponent;
  let inputEl: HTMLElement;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [TestComponent]
    });

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;
    inputEl = fixture.nativeElement.querySelector('input');
  });

  it('should focus the input element when appAutofocus is true', () => {
    component.isAutofocus = true;
    fixture.detectChanges(); // Triggers change detection and ngAfterViewInit

    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(document.activeElement).toBe(inputEl);
        resolve();
      }, 10);
    });
  });

  it('should not focus the input element when appAutofocus is false', () => {
    component.isAutofocus = false;
    fixture.detectChanges();

    return new Promise<void>((resolve) => {
      setTimeout(() => {
        expect(document.activeElement).not.toBe(inputEl);
        resolve();
      }, 10);
    });
  });
});
