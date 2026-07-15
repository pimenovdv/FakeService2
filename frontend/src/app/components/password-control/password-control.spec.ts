import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PasswordControlComponent } from './password-control';
import { StateService } from '../../services/state';
import { ComponentDef } from '../../models/screen.model';
import { FormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { vi, describe, it, expect, beforeEach } from 'vitest';

describe('PasswordControlComponent', () => {
  let component: PasswordControlComponent;
  let fixture: ComponentFixture<PasswordControlComponent>;
  let stateServiceMock: any;
  const mockDef: ComponentDef = {
    id: 'testPassword',
    type: 'password',
    label: 'Password',
    placeholder: 'Enter password'
  };

  beforeEach(async () => {
    stateServiceMock = {
      setValidation: vi.fn(),
      submitAttempted$: { subscribe: vi.fn() }
    };

    await TestBed.configureTestingModule({
      imports: [PasswordControlComponent, FormsModule],
      providers: [
        { provide: StateService, useValue: stateServiceMock }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(PasswordControlComponent);
    component = fixture.componentInstance;

    // Use setInput to properly update the Signal-based inputs or normal inputs before detectChanges
    fixture.componentRef.setInput('def', mockDef);
    fixture.componentRef.setInput('value', '');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render label and input', () => {
    const label = fixture.debugElement.query(By.css('label')).nativeElement;
    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    const button = fixture.debugElement.query(By.css('button')).nativeElement;

    expect(label.textContent).toContain('Password');
    expect(input.placeholder).toBe('Enter password');
    expect(input.type).toBe('password');
    expect(button.textContent).toContain('Show');
  });

  it('should toggle password visibility', () => {
    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    const button = fixture.debugElement.query(By.css('button'));

    expect(component.showPassword).toBe(false);
    expect(input.type).toBe('password');

    button.triggerEventHandler('click', null);
    fixture.detectChanges();

    expect(component.showPassword).toBe(true);
    expect(input.type).toBe('text');
    expect(button.nativeElement.textContent).toContain('Hide');

    button.triggerEventHandler('click', null);
    fixture.detectChanges();

    expect(component.showPassword).toBe(false);
    expect(input.type).toBe('password');
    expect(button.nativeElement.textContent).toContain('Show');
  });

  it('should validate required field', () => {
    const requiredDef: ComponentDef = {
      ...mockDef,
      validations: [{ type: 'required', message: 'Password is required' }]
    };
    fixture.componentRef.setInput('def', requiredDef);
    fixture.detectChanges();

    component.onValueChange('');
    expect(component.isValid).toBe(false);
    expect(component.errors).toContain('Password is required');

    component.onValueChange('secret');
    expect(component.isValid).toBe(true);
    expect(component.errors.length).toBe(0);
  });

  it('should disabled input and button when disabled', async () => {
    const disabledDef: ComponentDef = {
      ...mockDef,
      disabled: true
    };

    // We need to trigger change detection after setting both def and value
    fixture.componentRef.setInput('def', disabledDef);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const input = fixture.debugElement.query(By.css('input')).nativeElement;
    const button = fixture.debugElement.query(By.css('button')).nativeElement;

    expect(input.disabled).toBe(true);
    expect(button.disabled).toBe(true);
  });
});
