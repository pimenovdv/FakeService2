import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RadioControlComponent } from './radio-control';
import { ComponentDef } from '../../models/screen.model';
import { StateService } from '../../services/state';
import { BehaviorSubject } from 'rxjs';
import { expect, describe, it, beforeEach, vi } from 'vitest';
import { By } from '@angular/platform-browser';

describe('RadioControlComponent', () => {
  let component: RadioControlComponent;
  let fixture: ComponentFixture<RadioControlComponent>;
  let mockStateService: any;
  let getValidationMock: any;
  let setValidationMock: any;
  let submitAttemptedSubject: BehaviorSubject<boolean>;

  beforeEach(async () => {
    submitAttemptedSubject = new BehaviorSubject<boolean>(false);
    mockStateService = {
      submitAttempted$: submitAttemptedSubject.asObservable(),
      setValidation: vi.fn()
    };

    await TestBed.configureTestingModule({
      imports: [RadioControlComponent],
      providers: [
        { provide: StateService, useValue: mockStateService }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(RadioControlComponent);
    component = fixture.componentInstance;
    component.def = {
      id: 'testRadio',
      type: 'radio',
      label: 'Test Radio',
      options: [
        { label: 'Option 1', value: 'opt1' },
        { label: 'Option 2', value: 'opt2' }
      ]
    } as ComponentDef;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render radio options correctly based on options array (objects)', () => {
    const radioInputs = fixture.debugElement.queryAll(By.css('input[type="radio"]'));
    expect(radioInputs.length).toBe(2);

    expect(radioInputs[0].nativeElement.value).toBe('opt1');
    expect(radioInputs[1].nativeElement.value).toBe('opt2');

    const labels = fixture.debugElement.queryAll(By.css('.radio-option label'));
    expect(labels[0].nativeElement.textContent).toBe('Option 1');
    expect(labels[1].nativeElement.textContent).toBe('Option 2');
  });

  it('should render radio options correctly based on options array (primitives)', () => {
    component.def.options = ['Apple', 'Banana'];
    fixture.detectChanges();

    const radioInputs = fixture.debugElement.queryAll(By.css('input[type="radio"]'));
    expect(radioInputs.length).toBe(2);

    expect(radioInputs[0].nativeElement.value).toBe('Apple');
    expect(radioInputs[1].nativeElement.value).toBe('Banana');

    const labels = fixture.debugElement.queryAll(By.css('.radio-option label'));
    expect(labels[0].nativeElement.textContent).toBe('Apple');
    expect(labels[1].nativeElement.textContent).toBe('Banana');
  });

  it('should emit valueChange when an option is selected', () => {
    vi.spyOn(component.valueChange, 'emit');

    const radioInputs = fixture.debugElement.queryAll(By.css('input[type="radio"]'));
    radioInputs[1].nativeElement.click(); // Click Option 2
    fixture.detectChanges();

    expect(component.value).toBe('opt2');
    expect(component.valueChange.emit).toHaveBeenCalledWith('opt2');
  });

  it('should disable radio buttons when def.disabled is true', () => {
    component.def.disabled = true;
    fixture.detectChanges();

    const radioInputs = fixture.debugElement.queryAll(By.css('input[type="radio"]'));
    expect(radioInputs[0].nativeElement.disabled).toBe(true);
    expect(radioInputs[1].nativeElement.disabled).toBe(true);
  });
});
