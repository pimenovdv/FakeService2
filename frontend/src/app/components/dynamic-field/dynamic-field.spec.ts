import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DynamicFieldComponent } from './dynamic-field.component';
import { ComponentDef } from '../../models/screen.model';
import { StateService } from '../../services/state';
import { BehaviorSubject } from 'rxjs';
import { vi, expect, describe, it, beforeEach } from 'vitest';

describe('DynamicFieldComponent', () => {
  let component: DynamicFieldComponent;
  let fixture: ComponentFixture<DynamicFieldComponent>;
  let mockStateService: any;
  let answersSubject: BehaviorSubject<Record<string, any>>;

  beforeEach(async () => {
    answersSubject = new BehaviorSubject<Record<string, any>>({});
    mockStateService = {
      answers$: answersSubject.asObservable(),
      evaluateCondition: vi.fn().mockReturnValue(false),
      getAllAnswers: vi.fn().mockReturnValue({}),
      setAnswer: vi.fn(),
      setValidation: vi.fn(),
      submitAttempted$: new BehaviorSubject(false).asObservable()
    };

    await TestBed.configureTestingModule({
      imports: [DynamicFieldComponent],
      providers: [
        { provide: StateService, useValue: mockStateService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DynamicFieldComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.componentDef = { id: 'test1', type: 'text', label: 'Test' } as ComponentDef;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should render text input component', () => {
    component.componentDef = { id: 'field1', type: 'text', label: 'Text Field' } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('app-text-input')).toBeTruthy();
  });

  it('should render fallback for unknown component type', () => {
    component.componentDef = { id: 'field2', type: 'unknown' as any, label: 'Unknown Field' } as ComponentDef;
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.fallback-field')?.textContent).toContain('Unsupported component type: unknown');
  });

  it('should reactively evaluate showIf conditions and update hidden state', () => {
    component.componentDef = {
      id: 'field3', type: 'text', label: 'Dependent',
      showIf: { field: 'otherField', operator: '==', value: 'show' }
    } as ComponentDef;

    mockStateService.evaluateCondition.mockReturnValue(true);
    fixture.detectChanges(); // initial evaluation via ngOnInit

    expect(component.isHidden).toBe(false);

    mockStateService.evaluateCondition.mockReturnValue(false);
    answersSubject.next({ otherField: 'hide' }); // trigger evaluation
    fixture.detectChanges();

    expect(component.isHidden).toBe(true);
  });

  it('should reactively evaluate disableIf conditions and update state', () => {
    component.componentDef = {
      id: 'field4', type: 'text', label: 'Dependent',
      disableIf: { field: 'otherField', operator: '==', value: 'disable' }
    } as ComponentDef;

    mockStateService.evaluateCondition.mockReturnValue(false);
    fixture.detectChanges();

    expect(component.isDisabled).toBe(false);

    mockStateService.evaluateCondition.mockReturnValue(true);
    answersSubject.next({ otherField: 'disable' });
    fixture.detectChanges();

    expect(component.isDisabled).toBe(true);
    expect(component.componentDef.disabled).toBe(true); // check if passed down
  });
});
