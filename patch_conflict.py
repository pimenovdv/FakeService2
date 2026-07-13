import os

with open("frontend/src/app/components/dynamic-field/dynamic-field.spec.ts", "r") as f:
    content = f.read()

resolved = """import { vitest } from "vitest";
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DynamicFieldComponent } from './dynamic-field.component';
import { ComponentDef } from '../../models/screen.model';
import { expect, describe, it, beforeEach } from 'vitest';
import { StateService } from '../../services/state';
import { of } from 'rxjs';

describe('DynamicFieldComponent', () => {
  let component: DynamicFieldComponent;
  let fixture: ComponentFixture<DynamicFieldComponent>;
  let mockStateService: any;

  beforeEach(async () => {
    mockStateService = {
      evaluateCondition: vitest.fn().mockReturnValue(false),
      answers$: of({}),
      submitAttempted$: of(false),
      setAnswer: vitest.fn(),
      setValidation: vitest.fn(),
      getAnswer: vitest.fn().mockReturnValue(null)
    };

    await TestBed.configureTestingModule({
      imports: [DynamicFieldComponent],
      providers: [{ provide: StateService, useValue: mockStateService }]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DynamicFieldComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.componentDef = { id: 'test', type: 'text', label: 'Test' };
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should render fallback for unknown component type', () => {
    component.componentDef = {
      id: 'unknown-id',
      type: 'unknown' as any,
      label: 'Unknown Field'
    } as ComponentDef;

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Unsupported component type: unknown (ID: unknown-id)');
  });

  it('should render text input component', () => {
    component.componentDef = {
      id: 'test_text_id',
      type: 'text',
      label: 'Test Text Field'
    } as ComponentDef;

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const textInput = compiled.querySelector('app-text-input');
    expect(textInput).toBeTruthy();
  });

  it('should reactively evaluate disableIf conditions and update state', async () => {
    component.componentDef = {
      id: 'conditional_field',
      type: 'text',
      label: 'Conditional Field',
      disableIf: { field: 'other_field', operator: '==', value: 'disable_me' }
    };
    fixture.detectChanges();
    expect(component.isDisabled).toBe(false);

    mockStateService.evaluateCondition.mockReturnValue(true);
    // Simulate answers$ emitting
    component['evaluateConditions']();

    expect(component.isDisabled).toBe(true);
    expect(component.componentDef.disabled).toBe(true);

    mockStateService.evaluateCondition.mockReturnValue(false);
    component['evaluateConditions']();

    expect(component.isDisabled).toBe(false);
    expect(component.componentDef.disabled).toBe(false);
  });

  it('should reactively evaluate showIf conditions and update hidden state', async () => {
    component.componentDef = {
      id: 'conditional_field_2',
      type: 'text',
      label: 'Conditional Field 2',
      showIf: { field: 'other_field', operator: '==', value: 'show_me' }
    };
    mockStateService.evaluateCondition.mockReturnValue(false);
    fixture.detectChanges();

    expect(component.isHidden).toBe(true);

    mockStateService.evaluateCondition.mockReturnValue(true);
    component['evaluateConditions']();
    expect(component.isHidden).toBe(false);
  });

  it('should call stateService.setAnswer on value change', () => {
    component.componentDef = { id: 'test_id', type: 'text', label: 'Test' } as ComponentDef;
    component.onValueChange('new value');
    expect(mockStateService.setAnswer).toHaveBeenCalledWith('test_id', 'new value');
  });

  it('should validate inner control', () => {
    component.componentDef = { id: 'test_id', type: 'text', label: 'Test' } as ComponentDef;
    const innerControlSpy = { touched: false, validate: vitest.fn(), isValid: false };
    component.innerControl = innerControlSpy as any;

    const result = component.validate();

    expect(innerControlSpy.touched).toBe(true);
    expect(innerControlSpy.validate).toHaveBeenCalled();
    expect(result).toBe(false);
  });
});"""

with open("frontend/src/app/components/dynamic-field/dynamic-field.spec.ts", "w") as f:
    f.write(resolved)
