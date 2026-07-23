import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EmailControlComponent } from './email-control';
import { StateService } from '../../services/state';
import { ComponentDef } from '../../models/screen.model';
import { By } from '@angular/platform-browser';
import { describe, it, expect, beforeEach } from 'vitest';

describe('EmailControlComponent', () => {
  let component: EmailControlComponent;
  let fixture: ComponentFixture<EmailControlComponent>;
  let stateService: StateService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EmailControlComponent],
      providers: [StateService]
    }).compileComponents();

    fixture = TestBed.createComponent(EmailControlComponent);
    component = fixture.componentInstance;
    stateService = TestBed.inject(StateService);

    const mockDef: ComponentDef = {
      id: 'email1',
      type: 'email',
      label: 'Email',
      validations: []
    };

    fixture.componentRef.setInput('def', mockDef);
    fixture.componentRef.setInput('value', '');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display the label', () => {
    const labelElement = fixture.debugElement.query(By.css('label')).nativeElement;
    expect(labelElement.textContent).toContain('Email');
  });

  it('should bind the value to the input', async () => {
    fixture.componentRef.setInput('value', 'test@example.com');
    fixture.detectChanges();
    await fixture.whenStable();

    const inputElement = fixture.debugElement.query(By.css('input')).nativeElement;
    expect(inputElement.value).toBe('test@example.com');
  });

  it('should call onValueChange when input changes', async () => {
    const inputElement = fixture.debugElement.query(By.css('input')).nativeElement;
    inputElement.value = 'new@example.com';
    inputElement.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    await fixture.whenStable();

    expect(component.value).toBe('new@example.com');
  });

  it('should be disabled when def.disabled is true', async () => {
    fixture.componentRef.setInput('def', { ...component.def, disabled: true });
    fixture.detectChanges();
    await fixture.whenStable();

    const inputElement = fixture.debugElement.query(By.css('input')).nativeElement;
    expect(inputElement.disabled).toBe(true);
  });

  it('should not render clear button when clearable is false', () => {
    fixture.componentRef.setInput('def', { ...component.def, clearable: false });
    component.value = 'test@example.com';
    fixture.detectChanges();

    const clearBtn = fixture.nativeElement.querySelector('.clear-button');
    expect(clearBtn).toBeNull();
  });

  it('should render clear button when clearable is true and value exists', () => {
    fixture.componentRef.setInput('def', { ...component.def, clearable: true });
    component.value = 'test@example.com';
    fixture.detectChanges();

    const clearBtn = fixture.nativeElement.querySelector('.clear-button');
    expect(clearBtn).toBeTruthy();
  });

  it('should clear value when clear button is clicked', () => {
    fixture.componentRef.setInput('def', { ...component.def, clearable: true });
    component.value = 'test@example.com';
    fixture.detectChanges();

    let emittedValue: any;
    component.valueChange.subscribe(val => emittedValue = val);

    const clearBtn = fixture.nativeElement.querySelector('.clear-button') as HTMLButtonElement;
    clearBtn.click();

    expect(emittedValue).toBe('');
    expect(component.value).toBe('');
  });
});
