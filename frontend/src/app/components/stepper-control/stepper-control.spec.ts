import { ComponentFixture, TestBed } from '@angular/core/testing';
import { StepperControlComponent } from './stepper-control';
import { ComponentDef } from '../../models/screen.model';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import { FormsModule } from '@angular/forms';

describe('StepperControlComponent', () => {
  let component: StepperControlComponent;
  let fixture: ComponentFixture<StepperControlComponent>;
  let baseDef: ComponentDef;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StepperControlComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(StepperControlComponent);
    component = fixture.componentInstance;

    baseDef = {
      id: 'stepper1',
      type: 'stepper',
      label: 'Quantity'
    };
  });

  it('should initialize with provided definition and value', async () => {
    fixture.componentRef.setInput('def', baseDef);
    fixture.componentRef.setInput('value', 5);
    fixture.detectChanges();
    await fixture.whenStable();

    const input = fixture.nativeElement.querySelector('.stepper-input');
    expect(input.value).toBe('5');
    expect(component.value).toBe(5);
  });

  it('should increment value', async () => {
    fixture.componentRef.setInput('def', baseDef);
    fixture.componentRef.setInput('value', 0);
    fixture.detectChanges();
    await fixture.whenStable();

    const incrementSpy = vi.spyOn(component.valueChange, 'emit');

    const incrementBtn = fixture.nativeElement.querySelector('.increment-btn');
    incrementBtn.click();
    fixture.detectChanges();

    expect(incrementSpy).toHaveBeenCalledWith(1);
  });

  it('should decrement value', async () => {
    fixture.componentRef.setInput('def', baseDef);
    fixture.componentRef.setInput('value', 5);
    fixture.detectChanges();
    await fixture.whenStable();

    const decrementSpy = vi.spyOn(component.valueChange, 'emit');

    const decrementBtn = fixture.nativeElement.querySelector('.decrement-btn');
    decrementBtn.click();
    fixture.detectChanges();

    expect(decrementSpy).toHaveBeenCalledWith(4);
  });

  it('should increment value by step', async () => {
    const defWithStep = { ...baseDef, validations: [{ type: 'step' as any, value: 5 }] };
    fixture.componentRef.setInput('def', defWithStep);
    fixture.componentRef.setInput('value', 0);
    fixture.detectChanges();
    await fixture.whenStable();

    const incrementSpy = vi.spyOn(component.valueChange, 'emit');

    const incrementBtn = fixture.nativeElement.querySelector('.increment-btn');
    incrementBtn.click();
    fixture.detectChanges();

    expect(incrementSpy).toHaveBeenCalledWith(5);
  });

  it('should decrement value by step', async () => {
    const defWithStep = { ...baseDef, validations: [{ type: 'step' as any, value: 3 }] };
    fixture.componentRef.setInput('def', defWithStep);
    fixture.componentRef.setInput('value', 10);
    fixture.detectChanges();
    await fixture.whenStable();

    const decrementSpy = vi.spyOn(component.valueChange, 'emit');

    const decrementBtn = fixture.nativeElement.querySelector('.decrement-btn');
    decrementBtn.click();
    fixture.detectChanges();

    expect(decrementSpy).toHaveBeenCalledWith(9);
  });

  it('should snap to closest valid step on increment when not on step', async () => {
    const defWithStep = { ...baseDef, validations: [{ type: 'step' as any, value: 5 }, { type: 'min' as any, value: 2 }] };
    fixture.componentRef.setInput('def', defWithStep);
    fixture.componentRef.setInput('value', 4); // steps are 2, 7, 12, etc.
    fixture.detectChanges();
    await fixture.whenStable();

    const incrementSpy = vi.spyOn(component.valueChange, 'emit');
    component.increment();
    fixture.detectChanges();

    expect(incrementSpy).toHaveBeenCalledWith(7);
  });

  it('should respect min validation on decrement', async () => {
    const defWithMin = { ...baseDef, validations: [{ type: 'min' as any, value: 0 }] };
    fixture.componentRef.setInput('def', defWithMin);
    fixture.componentRef.setInput('value', 0);
    fixture.detectChanges();
    await fixture.whenStable();

    const decrementSpy = vi.spyOn(component.valueChange, 'emit');

    const decrementBtn = fixture.nativeElement.querySelector('.decrement-btn');
    // The button should be disabled via template, but let's test component logic too
    component.decrement();
    fixture.detectChanges();

    expect(decrementSpy).not.toHaveBeenCalled();
    expect(decrementBtn.disabled).toBe(true);
  });

  it('should respect max validation on increment', async () => {
    const defWithMax = { ...baseDef, validations: [{ type: 'max' as any, value: 10 }] };
    fixture.componentRef.setInput('def', defWithMax);
    fixture.componentRef.setInput('value', 10);
    fixture.detectChanges();
    await fixture.whenStable();

    const incrementSpy = vi.spyOn(component.valueChange, 'emit');

    const incrementBtn = fixture.nativeElement.querySelector('.increment-btn');
    // The button should be disabled via template, but let's test component logic too
    component.increment();
    fixture.detectChanges();

    expect(incrementSpy).not.toHaveBeenCalled();
    expect(incrementBtn.disabled).toBe(true);
  });

  it('should correct value on blur if outside bounds', async () => {
      const defWithBounds = { ...baseDef, validations: [{ type: 'min' as any, value: 0 }, { type: 'max' as any, value: 10 }] };
      fixture.componentRef.setInput('def', defWithBounds);
      fixture.componentRef.setInput('value', 15);
      fixture.detectChanges();
      await fixture.whenStable();

      const emitSpy = vi.spyOn(component.valueChange, 'emit');
      const input = fixture.nativeElement.querySelector('.stepper-input');

      input.dispatchEvent(new Event('blur'));

      expect(emitSpy).toHaveBeenCalledWith(10);
  });

  it('should correct NaN value on blur to 0', async () => {
      fixture.componentRef.setInput('def', baseDef);
      fixture.componentRef.setInput('value', 'invalid');
      fixture.detectChanges();
      await fixture.whenStable();

      const emitSpy = vi.spyOn(component.valueChange, 'emit');
      const input = fixture.nativeElement.querySelector('.stepper-input');

      input.dispatchEvent(new Event('blur'));

      expect(emitSpy).toHaveBeenCalledWith(0);
  });
});