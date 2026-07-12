import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DynamicFieldComponent } from './dynamic-field.component';
import { ComponentDef } from '../../models/screen.model';
import { expect, describe, it, beforeEach } from 'vitest';
import { StateService } from '../../services/state';

describe('DynamicFieldComponent', () => {
  let component: DynamicFieldComponent;
  let fixture: ComponentFixture<DynamicFieldComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DynamicFieldComponent]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DynamicFieldComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
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

  it('should hide component when hidden is true', () => {
    component.componentDef = {
      id: 'test_hidden_id',
      type: 'text',
      label: 'Hidden Field',
      hidden: true
    } as ComponentDef;

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('app-text-input')).toBeFalsy();
  });

  it('should evaluate showIf condition', () => {
    // Inject StateService and mock answer
    const stateService = TestBed.inject(StateService);
    stateService.setAnswer('other_field', 'yes');

    component.componentDef = {
      id: 'test_showif_id',
      type: 'text',
      label: 'Show If Field',
      showIf: { field: 'other_field', equals: 'yes' }
    } as ComponentDef;

    fixture.detectChanges();

    let compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('app-text-input')).toBeTruthy();

    stateService.setAnswer('other_field', 'no');
    fixture.detectChanges();

    expect(component.show).toBe(false);
  });

  it('should evaluate disableIf condition', () => {
    const stateService = TestBed.inject(StateService);
    stateService.setAnswer('disable_trigger', true);

    component.componentDef = {
      id: 'test_disableif_id',
      type: 'text',
      label: 'Disable If Field',
      disableIf: { field: 'disable_trigger', equals: true }
    } as ComponentDef;

    fixture.detectChanges();

    expect(component.isDisabled).toBe(true);

    stateService.setAnswer('disable_trigger', false);
    fixture.detectChanges();

    expect(component.isDisabled).toBe(false);
  });
});
