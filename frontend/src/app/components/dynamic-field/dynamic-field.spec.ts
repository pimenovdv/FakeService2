import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DynamicFieldComponent } from './dynamic-field.component';
import { ComponentDef } from '../../models/screen.model';
import { StateService } from '../../services/state';
import { expect, describe, it, beforeEach } from 'vitest';

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

  it('should be hidden when showIf condition is not met', () => {
    component.componentDef = {
      id: 'test_id',
      type: 'text',
      label: 'Test Field',
      showIf: { componentId: 'other_id', value: 'show' }
    } as ComponentDef;

    fixture.detectChanges(); // StateService initially has empty answers
    expect(component.isVisible).toBeFalsy();

    const compiled = fixture.nativeElement as HTMLElement;
    const container = compiled.querySelector('.dynamic-field-container');
    expect(container).toBeNull();
  });

  it('should be visible when showIf condition is met', () => {
    component.componentDef = {
      id: 'test_id',
      type: 'text',
      label: 'Test Field',
      showIf: { componentId: 'other_id', value: 'show' }
    } as ComponentDef;

    const stateService = TestBed.inject(StateService);
    stateService.setAnswer('other_id', 'show');

    fixture.detectChanges();
    expect(component.isVisible).toBeTruthy();

    const compiled = fixture.nativeElement as HTMLElement;
    const container = compiled.querySelector('.dynamic-field-container');
    expect(container).toBeTruthy();
  });

  it('should pass disabled state down to control when disableIf condition is met', async () => {
    component.componentDef = {
      id: 'test_id',
      type: 'text',
      label: 'Test Field',
      disableIf: { componentId: 'other_id', value: 'disable' }
    } as ComponentDef;

    const stateService = TestBed.inject(StateService);
    stateService.setAnswer('other_id', 'disable');

    fixture.detectChanges();
    await fixture.whenStable(); // wait for rendering of sub-components

    expect(component.componentDef.disabled).toBeTruthy();

    const compiled = fixture.nativeElement as HTMLElement;
    const input = compiled.querySelector('input');
    expect(input?.disabled).toBeTruthy();
  });
});
