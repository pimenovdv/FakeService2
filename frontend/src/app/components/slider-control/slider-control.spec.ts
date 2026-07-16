import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SliderControlComponent } from './slider-control';
import { ComponentDef } from '../../models/screen.model';
import { By } from '@angular/platform-browser';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('SliderControlComponent', () => {
  let component: SliderControlComponent;
  let fixture: ComponentFixture<SliderControlComponent>;

  const mockDef: ComponentDef = {
    id: 'test-slider',
    type: 'slider',
    label: 'Test Slider',
    validations: [
      { type: 'min', value: 10 },
      { type: 'max', value: 50 }
    ]
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SliderControlComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(SliderControlComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('def', mockDef);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render range input with correct min and max', () => {
    const inputEl = fixture.debugElement.query(By.css('input[type="range"]')).nativeElement;
    expect(inputEl.min).toBe('10');
    expect(inputEl.max).toBe('50');
  });

  it('should emit value change on input change', () => {
    vi.spyOn(component.valueChange, 'emit');
    const inputEl = fixture.debugElement.query(By.css('input[type="range"]')).nativeElement;

    // Simulate user changing the slider
    inputEl.value = '25';
    inputEl.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    // The ngModelChange might fire on input or change depending on browser,
    // but in Angular tests with FormsModule, dispatching 'input' triggers it.
    expect(component.valueChange.emit).toHaveBeenCalledWith(25);
  });

  it('should format value in the template', () => {
    fixture.componentRef.setInput('value', 42);
    fixture.detectChanges();

    const valueSpan = fixture.debugElement.query(By.css('.slider-value')).nativeElement;
    expect(valueSpan.textContent.trim()).toBe('42');
  });

  it('should apply disabled state', () => {
    fixture.componentRef.setInput('def', { ...mockDef, disabled: true });
    fixture.detectChanges();

    const inputEl = fixture.debugElement.query(By.css('input[type="range"]')).nativeElement;
    expect(inputEl.disabled).toBe(true);
  });
});
