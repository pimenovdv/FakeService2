import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MaskDirective } from './mask.directive';

@Component({
  template: `
    <input type="text" [appMask]="mask" [(ngModel)]="value" />
  `,
  standalone: true,
  imports: [FormsModule, MaskDirective]
})
class TestMaskComponent {
  mask?: string = '(000) 000-0000';
  value: string = '';
}

describe('MaskDirective', () => {
  let component: TestMaskComponent;
  let fixture: ComponentFixture<TestMaskComponent>;
  let inputEl: HTMLInputElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestMaskComponent, MaskDirective, FormsModule, ReactiveFormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(TestMaskComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    inputEl = fixture.nativeElement.querySelector('input');
  });

  it('should format phone number correctly', async () => {
    inputEl.value = '1234567890';
    inputEl.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(inputEl.value).toBe('(123) 456-7890');
    expect(component.value).toBe('(123) 456-7890');
  });

  it('should ignore letters for number mask', async () => {
    inputEl.value = '12a34b567890';
    inputEl.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(inputEl.value).toBe('(123) 456-7890');
  });

  it('should format custom masks with letters', async () => {
    component.mask = 'AA-000';
    fixture.detectChanges();

    inputEl.value = 'AB123';
    inputEl.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(inputEl.value).toBe('AB-123');
  });

  it('should do nothing if mask is not provided', async () => {
    component.mask = undefined;
    fixture.detectChanges();

    inputEl.value = '12345';
    inputEl.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(inputEl.value).toBe('12345');
  });

  it('should truncate input if it exceeds mask length', async () => {
      inputEl.value = '1234567890123';
      inputEl.dispatchEvent(new Event('input'));
      fixture.detectChanges();
      await fixture.whenStable();

      expect(inputEl.value).toBe('(123) 456-7890');
  });
});