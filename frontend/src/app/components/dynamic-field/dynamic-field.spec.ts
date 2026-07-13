import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DynamicFieldComponent } from './dynamic-field.component';
import { ComponentDef } from '../../models/screen.model';
import { expect, describe, it, beforeEach } from 'vitest';
import { StateService } from '../../services/state';

describe('DynamicFieldComponent', () => {
  let component: DynamicFieldComponent;
  let fixture: ComponentFixture<DynamicFieldComponent>;
  let stateService: StateService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DynamicFieldComponent],
      providers: [StateService]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DynamicFieldComponent);
    component = fixture.componentInstance;
    stateService = TestBed.inject(StateService);
  });

  it('should proxy value changes to state service', () => {
    component.componentDef = { id: 'test_field', type: 'text', label: 'Test' };
    fixture.detectChanges();

    component.onValueChange('new_value');
    expect(stateService.getAnswer('test_field')).toBe('new_value');
  });

  it('should proxy validity changes to state service', () => {
    component.componentDef = { id: 'test_field', type: 'text', label: 'Test' };
    fixture.detectChanges();

    component.onValidityChange(false);
    expect(stateService.isScreenValid()).toBe(false);

    component.onValidityChange(true);
    expect(stateService.isScreenValid()).toBe(true);
  });

  it('should force validity to true if field is hidden or disabled, and restore when visible', () => {
    component.componentDef = { id: 'test_field', type: 'text', label: 'Test' };
    fixture.detectChanges();

    component.onValidityChange(false); // child reports invalid
    expect(stateService.isScreenValid()).toBe(false); // initially false

    component.isHidden = true;
    component['updateValidationState'](); // trigger internal update as if evaluated
    expect(stateService.isScreenValid()).toBe(true); // forced true because hidden

    component.isHidden = false;
    component['updateValidationState']();
    expect(stateService.isScreenValid()).toBe(false); // restored to false
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

    stateService.setAnswer('other_field', 'disable_me');
    await fixture.whenStable();
    fixture.detectChanges();

    expect(component.isDisabled).toBe(true);
    expect(component.componentDef.disabled).toBe(true);

    stateService.setAnswer('other_field', 'dont_disable');
    await fixture.whenStable();
    fixture.detectChanges();

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
    fixture.detectChanges();
    // initially other_field is undefined, so showIf is false -> isHidden should be true
    expect(component.isHidden).toBe(true);

    stateService.setAnswer('other_field', 'show_me');
    await fixture.whenStable();
    fixture.detectChanges();
    expect(component.isHidden).toBe(false);
  });
});
