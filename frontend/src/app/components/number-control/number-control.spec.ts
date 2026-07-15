import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NumberControlComponent } from './number-control';
import { StateService } from '../../services/state';
import { ComponentDef } from '../../models/screen.model';
import { FormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('NumberControlComponent', () => {
  let component: NumberControlComponent;
  let fixture: ComponentFixture<NumberControlComponent>;
  let stateServiceMock: any;

  beforeEach(async () => {
    stateServiceMock = {
      setValidation: vi.fn(),
      submitAttempted$: { subscribe: vi.fn() }
    };

    await TestBed.configureTestingModule({
      imports: [NumberControlComponent, FormsModule],
      providers: [
        { provide: StateService, useValue: stateServiceMock }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(NumberControlComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.def = { id: 'num1', type: 'number', label: 'Age' } as ComponentDef;
    fixture.detectChanges();
    expect(component).toBeTruthy();
  });

  it('should render label and input', () => {
    component.def = { id: 'num1', type: 'number', label: 'Age', placeholder: 'Enter age' } as ComponentDef;
    fixture.detectChanges();

    const label = fixture.debugElement.query(By.css('label')).nativeElement;
    expect(label.textContent.trim()).toBe('Age');

    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    expect(input.type).toBe('number');
    expect(input.placeholder).toBe('Enter age');
  });

  it('should emit value change on input', () => {
    component.def = { id: 'num1', type: 'number', label: 'Age' } as ComponentDef;
    fixture.detectChanges();

    const valueChangeSpy = vi.spyOn(component.valueChange, 'emit');

    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    input.value = '42';
    input.dispatchEvent(new Event('input'));



    // the value is string because ngModel binds to string for input type number by default
    // We expect valueChange to emit the value
    expect(valueChangeSpy).toHaveBeenCalledWith(42);
  });

  it('should trigger validation on blur', () => {
    component.def = {
      id: 'num1',
      type: 'number',
      label: 'Age',
      validations: [{ type: 'required', message: 'Required field' }]
    } as ComponentDef;
    fixture.detectChanges();

    expect(component.touched).toBeFalsy();

    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    input.dispatchEvent(new Event('blur'));


    fixture.detectChanges();

    expect(component.touched).toBeTruthy();
    expect(component.isValid).toBeFalsy();

    const errors = fixture.debugElement.queryAll(By.css('.error-text'));
    expect(errors.length).toBe(1);
    expect(errors[0].nativeElement.textContent.trim()).toBe('Required field');
  });

  it('should enforce min and max validations', () => {
    component.def = {
      id: 'num1',
      type: 'number',
      label: 'Age',
      validations: [
        { type: 'min', value: 18, message: 'Too young' },
        { type: 'max', value: 65, message: 'Too old' }
      ]
    } as ComponentDef;
    fixture.detectChanges();

    component.onValueChange(17);
    expect(component.isValid).toBeFalsy();
    expect(component.errors).toContain('Too young');

    component.onValueChange(66);
    expect(component.isValid).toBeFalsy();
    expect(component.errors).toContain('Too old');

    component.onValueChange(30);
    expect(component.isValid).toBeTruthy();
    expect(component.errors.length).toBe(0);
  });
});
