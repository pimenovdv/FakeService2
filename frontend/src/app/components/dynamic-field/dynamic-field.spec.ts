import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DynamicFieldComponent } from './dynamic-field.component';
import { ComponentDef } from '../../models/screen.model';
import { StateService } from '../../services/state';
import { expect, describe, it, beforeEach } from 'vitest';

describe('DynamicFieldComponent', () => {
  let component: DynamicFieldComponent;
  let fixture: ComponentFixture<DynamicFieldComponent>;

  let mockStateService: any;
  beforeEach(async () => {
    mockStateService = {
      evaluateDependencies: vi.fn().mockReturnValue(true),
      setValidationState: vi.fn()
    };
    await TestBed.configureTestingModule({
      imports: [DynamicFieldComponent],
      providers: [
        { provide: StateService, useValue: mockStateService }
      ]
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

  it('should forward validation state to StateService', () => {
    component.componentDef = { id: 'test_id', type: 'text', label: 'L' } as ComponentDef;
    component.onValidationChange(false);
    expect(mockStateService.setValidationState).toHaveBeenCalledWith('test_id', false);
  });
});
