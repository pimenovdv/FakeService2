import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TextInputComponent } from './text-input';
import { FormsModule } from '@angular/forms';
import { ComponentDef } from '../../models/screen.model';
import { expect, describe, it, beforeEach } from 'vitest';

describe('TextInputComponent', () => {
  let component: TextInputComponent;
  let fixture: ComponentFixture<TextInputComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextInputComponent, FormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(TextInputComponent);
    component = fixture.componentInstance;

    // Provide a mock component definition
    const mockDef: ComponentDef = {
      id: 'test_text',
      type: 'text',
      label: 'Test Label',
      placeholder: 'Test Placeholder',
      validations: [
        { type: 'required', message: 'Required field' }
      ]
    };
    component.def = mockDef;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should render label and input', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    const label = compiled.querySelector('label');
    const input = compiled.querySelector('input');

    expect(label?.textContent).toContain('Test Label');
    expect(input?.placeholder).toBe('Test Placeholder');
  });

  it('should show error when touched and invalid', () => {
    component.touched = true;
    component.value = '';
    component.validate();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const errorText = compiled.querySelector('.error-text');
    expect(errorText?.textContent?.trim()).toBe('Required field');
  });

  it('should render character count when maxLength is set', () => {
    component.def = {
      ...component.def,
      validations: [
        { type: 'maxLength', value: 10 }
      ]
    };
    component.value = 'hello';
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const charCount = compiled.querySelector('.character-count');

    expect(charCount).toBeTruthy();
    expect(charCount?.textContent?.trim()).toBe('5 / 10');
  });

  it('should not render character count when maxLength is not set', () => {
    component.def = {
      ...component.def,
      validations: []
    };
    component.value = 'hello';
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    const charCount = compiled.querySelector('.character-count');

    expect(charCount).toBeNull();
  });
});
