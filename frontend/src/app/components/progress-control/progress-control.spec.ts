import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ProgressControlComponent } from './progress-control';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('ProgressControlComponent', () => {
  let component: ProgressControlComponent;
  let fixture: ComponentFixture<ProgressControlComponent>;

  const mockDef: ComponentDef = {
    id: 'test-progress',
    type: 'progress',
    label: 'Test Progress',
    validations: [{ type: 'required' }]
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProgressControlComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(ProgressControlComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('def', mockDef);
    fixture.componentRef.setInput('value', 50);
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render label and required asterisk', () => {
    const labelEl = fixture.nativeElement.querySelector('label');
    expect(labelEl.textContent).toContain('Test Progress');
    expect(labelEl.textContent).toContain('*');
  });

  it('should correctly calculate getNumericValue', () => {
    expect(component.getNumericValue()).toBe(50);

    fixture.componentRef.setInput('value', null);
    expect(component.getNumericValue()).toBe(0);

    fixture.componentRef.setInput('value', '');
    expect(component.getNumericValue()).toBe(0);

    fixture.componentRef.setInput('value', undefined);
    expect(component.getNumericValue()).toBe(0);
  });

  it('should handle onClick event and update value', () => {
    const spy = vi.spyOn(component, 'onValueChange');
    const progressEl = fixture.nativeElement.querySelector('progress');

    // Mock getBoundingClientRect
    progressEl.getBoundingClientRect = vi.fn().mockReturnValue({
      left: 0,
      width: 100,
      top: 0,
      height: 20,
      bottom: 20,
      right: 100,
      x: 0,
      y: 0,
      toJSON: () => {}
    });

    const mockEvent = new MouseEvent('click', { clientX: 75 });
    component.onClick(mockEvent);

    expect(component.touched).toBe(true);
    expect(spy).toHaveBeenCalledWith(75);
    expect(component.value).toBe(75);
  });

  it('should not handle onClick event if disabled', () => {
    const disabledDef = { ...mockDef, disabled: true };
    fixture.componentRef.setInput('def', disabledDef);
    fixture.detectChanges();

    const spy = vi.spyOn(component, 'onValueChange');

    const mockEvent = new MouseEvent('click', { clientX: 75 });
    component.onClick(mockEvent);

    expect(component.touched).toBe(false);
    expect(spy).not.toHaveBeenCalled();
  });
});
